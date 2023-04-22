using Neo4j.Driver;
using ElectraArt_API.Exceptions;

#pragma warning disable 1591

namespace ElectraArt_API.Services
{
    public class GlobalUpvoteManger
    {
        private readonly IDriver _driver;
        public GlobalUpvoteManger(IDriver driver)
        {
            _driver = driver;
        }
        public async Task<Dictionary<string, object>[]> giveArtUpvote(long? v_discoUserId, string? v_discoUserName, long? v_discoArtId, long? v_upvoteGuild)
        {
            await using var session = _driver.AsyncSession();
            if ((v_discoUserId != null) && (v_discoArtId != null) && (v_discoUserName != null) && (v_upvoteGuild != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)<-[r1:CREATED]-(m:GlobalUser)
                    WHERE n.discoArtId = {v_discoArtId} AND r1.creationGuild = {v_upvoteGuild}
                    MATCH (x:GlobalUser)
                    WHERE x.discoUserId = {v_discoUserId}  AND x.discoUserName = '{v_discoUserName}'
                    WITH n,m,x
                    WHERE NOT EXISTS {{ MATCH (x)-[r2:UPVOTED]->(n) RETURN r2 }}
                    MERGE (x)-[r2:UPVOTED]->(n)
                    ON CREATE
                        SET r2.upvoteDate = timestamp()
                        SET r2.upvoteGuild = {v_upvoteGuild}
                        SET m.upvotes = m.upvotes + 1
                    RETURN r2 {{ .* }} AS upvote_found";
                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["upvote_found"].As<Dictionary<string, object>>())
                        .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid discord user id, art id, upvote date, and upvote guild to upvote an art");
            }
        }


    }
}
