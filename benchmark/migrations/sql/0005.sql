-- EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
DROP VIEW IF EXISTS v_benchmark_result_price_progress;
CREATE OR REPLACE VIEW v_benchmark_result_price_progress AS
  WITH first AS (
      SELECT
        test_case_id,
        MIN(x_created) AS first
      FROM benchmark_result
      GROUP BY test_case_id
  ), last AS (
      SELECT
        test_case_id,
        MAX(x_created) AS last
      FROM benchmark_result
      GROUP BY test_case_id
  ), days AS (
      SELECT
        id                                                                AS test_case_id,
        generate_series(first.first, last.last, INTERVAL '1 DAY') :: DATE AS day
      FROM benchmark_testcase
        INNER JOIN first ON first.test_case_id = id
        INNER JOIN last ON last.test_case_id = id
    -- WHERE section = '01_basic' AND name = '01'
  ), best_results AS (
      SELECT
        days.test_case_id                                       AS test_case_id,
        benchmark_team.id                                       AS team_id,
        days.day                                                AS day,
        MIN(operand_price + benchmark_result.instruction_price) AS price
      FROM
        benchmark_result
        INNER JOIN days
          ON days.test_case_id = benchmark_result.test_case_id AND
             days.day = benchmark_result.x_created :: DATE
        INNER JOIN benchmark_resultauthor ON benchmark_result.author_id = benchmark_resultauthor.id
        INNER JOIN benchmark_team ON benchmark_resultauthor.team_id = benchmark_team.id
      GROUP BY days.test_case_id, benchmark_team.id, days.day
  ), best_results_normalized AS (
      SELECT
        days.test_case_id,
        best_results.team_id,
        days.day,
        COALESCE(price, NULL) AS price
      FROM days
        LEFT JOIN best_results ON days.test_case_id = best_results.test_case_id AND
                                  best_results.day = days.day
  ) SELECT
      test_case_id            AS id,
      test_case_id,
      best_results_normalized.day,
      array_agg(leader_login) AS team_leader_logins,
      array_agg(price)        AS prices
    FROM best_results_normalized
      LEFT JOIN benchmark_team ON best_results_normalized.team_id = benchmark_team.id
    GROUP BY best_results_normalized.test_case_id, best_results_normalized.day
    HAVING COUNT(id) > 0;
