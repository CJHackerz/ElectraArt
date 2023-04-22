using Neo4j.Driver;
using ElectraArt_API.Exceptions;

#pragma warning disable 1591

namespace ElectraArt_API.Services
{
    public class GlobalUser
    {
        private readonly IDriver _driver;

        public GlobalUser(IDriver driver)
        {
            _driver = driver;
        
        }

        public async Task<Dictionary<string, object>[]> findMember(long? v_discoUserId)
        {
            await using var session = _driver.AsyncSession();
            if ((v_discoUserId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
            {
                var cypher = $@"
                MATCH (n:GlobalUser)
                WHERE n.discoUserId = {v_discoUserId}
                RETURN n {{ .* }} AS member_found";

                var cursor = await tx.RunAsync(cypher);
                var records = await cursor.ToListAsync();

                return records
                    .Select(x => x["member_found"].As<Dictionary<string, object>>())
                    .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid discord user id to lookup a member");
            }
        }

        public async Task<Dictionary<string, object>[]> getRecentGuild(long? v_discoUserId)
        {
            await using var session = _driver.AsyncSession();
            if ((v_discoUserId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
            {
                var cypher = $@"
                MATCH (:GlobalUser)-[r:CREATED]
                WHERE n.discoUserId = {v_discoUserId}
                RETURN n.recentArtSRC AS recent_guild_found";

                var cursor = await tx.RunAsync(cypher);
                var records = await cursor.ToListAsync();

                return records
                    .Select(x => x["recent_guild_found"].As<Dictionary<string, object>>())
                    .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid discord user id to lookup a member");
            }
        }

       //write code to update member's score in the global scoreboard
        public async Task<Dictionary<string, object>[]> newMember(long v_discoUserId, string? v_discoUserName)
        {
            await using var session = _driver.AsyncSession();
            if ((v_discoUserName != null)  && (v_discoUserId != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    CREATE (p:GlobalUser {{discoUserId: {v_discoUserId}, discoUserName: '{v_discoUserName}', recentArtSRC: 'unknown', upvotes: 0}})
                    RETURN p {{ .* }} AS new_member";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["new_member"].As<Dictionary<string, object>>())
                        .ToArray();
                    });
            }
            else {
                throw new ValidationException("Invalid parameters", "Please provide both required parameters, a valid discord user id and a valid discord user name");
            }
        }
        public async Task<Dictionary<string, object>[]> updateMember(long? v_discoUserId, string? v_discoUserName, long? v_recentArtSource, int? v_upvotesCount)
        {
            await using var session = _driver.AsyncSession();

            if ((v_recentArtSource == 0) && (v_upvotesCount != 0) && (v_discoUserId != null) && (v_discoUserName != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (p:GlobalUser)
                    WHERE p.discoUserId = {v_discoUserId} and p.discoUserName = '{v_discoUserName}'
                    SET p.upvotes = {v_upvotesCount}
                    RETURN p {{ .* }} AS new_member";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["new_member"].As<Dictionary<string, object>>())
                        .ToArray();
                    });
            }
            else if ((v_upvotesCount == 0) && (v_discoUserId != null) && (v_discoUserName != null) && (v_recentArtSource != 0)) {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    Match (p:GlobalUser)
                    WHERE p.discoUserId = {v_discoUserId} and p.discoUserName = '{v_discoUserName}'
                    SET p.recentArtSRC = {v_recentArtSource}
                    RETURN p {{ .* }} AS new_member";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["new_member"].As<Dictionary<string, object>>())
                        .ToArray();
                    });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide one of the both required parameters, a valid discord guild id for recent art source or a valid upvotes count");
            }
        }
    }   
}