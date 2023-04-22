using Neo4j.Driver;
using ElectraArt_API.Exceptions;

#pragma warning disable 1591

namespace ElectraArt_API.Services
{
    public class GlobalArt
    {
        private readonly IDriver _driver;

        public GlobalArt(IDriver driver)
        {
            _driver = driver;

        }

        public async Task<Dictionary<string, object>[]> findArt(long? v_discoArtId)
        {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)
                    WHERE n.discoArtId = {v_discoArtId}
                    RETURN n {{ .* }} AS art_found";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["art_found"].As<Dictionary<string, object>>())
                        .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid art id to lookup an Art");
            }
        }

        public async Task<List<string>> getArtTitle(long? v_discoArtId)
        {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)
                    WHERE n.discoArtId = {v_discoArtId}
                    RETURN n.title AS art_title_found";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records.Select(x => x["art_title_found"].As<string>())
                    .ToList();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid art id to lookup an Art Title");
            }
        }

        public async Task<List<string>> getArtCreatedBy(long? v_discoArtId)
        {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)
                    WHERE n.discoArtId = {v_discoArtId}
                    RETURN n.createdBy AS art_createdBy_found";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records.Select(x => x["art_createdBy_found"].As<string>())
                    .ToList();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid art id to lookup an Art Artist");
            }
        }

        public async Task<List<string>> getArtUrl(long? v_discoArtId) {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null))
            {
                return await session.ExecuteReadAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)
                    WHERE n.discoArtId = {v_discoArtId}
                    RETURN n.cdnUrl AS art_url_found";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();
                    
                    return records
                        .Select(x => x["art_url_found"].As<string>())
                        .ToList();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid art id to lookup an Art URL");
            }
        }

        public async Task<List<string>> updateArtUrl(long? v_discoArtId, string v_cdnUrl) {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    MATCH (n:GlobalArt)
                    WHERE n.discoArtId = {v_discoArtId}
                    SET n.cdnUrl = '{v_cdnUrl}'
                    RETURN n.cdnUrl AS art_url_found";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["art_url_found"].As<string>())
                        .ToList();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "Please provide a valid art id to update an Art URL");
            }
        }

        public async Task<Dictionary<string, object> []> newArt(long? v_discoArtId, string v_title, string v_cdnUrl, long? v_createdBy)
        {
            await using var session = _driver.AsyncSession();
            if((v_discoArtId != null) && (v_title != null) && (v_createdBy != null) && (v_cdnUrl != null))
            {
                return await session.ExecuteWriteAsync(async tx =>
                {
                    var cypher = $@"
                    CREATE (n:GlobalArt {{discoArtId: {v_discoArtId}, title: '{v_title}', createdBy: '{v_createdBy}', cdnUrl: '{v_cdnUrl}'}})
                    RETURN n {{ .* }} AS art_created";

                    var cursor = await tx.RunAsync(cypher);
                    var records = await cursor.ToListAsync();

                    return records
                        .Select(x => x["art_created"].As<Dictionary<string, object>>())
                        .ToArray();
                });
            }
            else
            {
                throw new ValidationException("Invalid parameters", "All required parameters must be provided to create a new Art");
            }
        }
    }       
}
