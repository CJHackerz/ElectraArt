using Neo4j.Driver;
using ElectraArt_API.Exceptions;

#pragma warning disable 1591

namespace ElectraArt_API.Services
{
    public class GlobalRelation
    {
        private readonly IDriver _driver;
        public GlobalRelation(IDriver driver)
        {
            _driver = driver;
        }
        public async Task<Dictionary<string, object>[]> userGenArt(long? v_discoUserId, long? v_discoArtId, long? v_creationDate, long? v_creationGuild)
        {
            await using var session = _driver.AsyncSession();
            if ((v_discoUserId != null) && (v_discoArtId != null) && (v_creationDate != null) && (v_creationGuild != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalUser), (m:GlobalArt)
                    WHERE n.discoUserId = {v_discoUserId} AND m.discoArtId = {v_discoArtId}
                    CREATE (n)-[r:CREATED]->(m)
                    SET r.creationDate = {v_creationDate}, r.creationGuild = {v_creationGuild}
                    RETURN r {{ .* }} AS relation_found";
                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();
                    return records
                        .Select(x => x["relation_found"].As<Dictionary<string, object>>())
                        .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide valid linkable parameters to create a relation between a user generated art");
            }
        } 
    }
}
