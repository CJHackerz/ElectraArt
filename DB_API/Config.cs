#pragma warning disable 1591
namespace ElectraArt_API
{
    public static class Config
    {
        private static readonly string Neo4jUri;
        private static readonly string Neo4jUsername;
        private static readonly string Neo4jPassword;


        static Config()
        {
            var config = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();

            var neo4j = config.GetSection("Neo4j");
            Neo4jUri = Environment.GetEnvironmentVariable("NEO4J_URI");
            Neo4jUsername = Environment.GetEnvironmentVariable("NEO4J_USERNAME");
            Neo4jPassword = Environment.GetEnvironmentVariable("NEO4J_PASSWORD");

        }

        public static (string Uri, string Username, string Password) UnpackNeo4jConfig()
        {
            return (Neo4jUri, Neo4jUsername, Neo4jPassword);
        }
    }
}