DROP VIEW IF EXISTS v_team_last_result;
CREATE OR REPLACE VIEW v_team_last_result AS
  SELECT
    benchmark_team.id               AS "id",
    benchmark_team.id               AS "team_id",
    MAX(benchmark_result.x_created) AS "last_result",
    count(benchmark_result.id)      AS "result_count"

  FROM benchmark_result
    INNER JOIN benchmark_resultauthor ON benchmark_result.author_id = benchmark_resultauthor.id
    INNER JOIN benchmark_team ON benchmark_resultauthor.team_id = benchmark_team.id
  GROUP BY benchmark_team.id;
