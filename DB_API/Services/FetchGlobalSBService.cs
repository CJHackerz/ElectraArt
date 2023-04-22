using Neo4j.Driver;
using ElectraArt_API.Exceptions;

#pragma warning disable 1591

namespace ElectraArt_API.Services
{
    public class FetchGlobalSB
    {
        private readonly IDriver _driver;

        public FetchGlobalSB(IDriver driver)
        {
            _driver = driver;

        }

        public async Task<Dictionary<string, object>[]> GlobalTop10()
        {
            await using var session = _driver.AsyncSession();

            return await session.ExecuteReadAsync(async tx =>
            {
                var cypher = $@"
                MATCH (p:GlobalUser)
                WITH p order by p.upvotes DESC
                RETURN p {{ .* }} AS scoreboard_t10
                LIMIT 10";

                var cursor = await tx.RunAsync(cypher);
                var records = await cursor.ToListAsync();

                return records
                    .Select(x => x["scoreboard_t10"].As<Dictionary<string, object>>())
                    .ToArray();
                });
        }
    }       
}
