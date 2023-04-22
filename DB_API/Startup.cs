using Neo4j.Driver;
using ElectraArt_API.Services;
using Microsoft.OpenApi.Models;
using System.Reflection;

#pragma warning disable 1591
public class Startup
{
    public Startup(IConfiguration configuration)
    {
        Configuration = configuration;
    }

    public IConfiguration Configuration { get; }

    public void ConfigureServices(IServiceCollection services)
    {
        var dbConfig = ElectraArt_API.Config.UnpackNeo4jConfig();
        services.AddSingleton<IDriver>(provider => GraphDatabase.Driver(dbConfig.Uri, 
            AuthTokens.Basic(dbConfig.Username, dbConfig.Password)));

        services.AddSingleton<GlobalUser>();
        services.AddSingleton<GlobalArt>();
        services.AddSingleton<GlobalRelation>();
        services.AddSingleton<GlobalUpvoteManger>();
        services.AddSingleton<FetchGlobalSB>();
        services.AddControllers();
        services.AddSwaggerGen(c =>
    {
        c.SwaggerDoc("v1", new OpenApiInfo { Title = "ElectraArt API Docs", Version = "v1.5" });

        var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
        var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
        c.IncludeXmlComments(xmlPath);
    });

   
    }

    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
        {
            app.UseDeveloperExceptionPage();
        }

        app.UseRouting();

        app.UseEndpoints(endpoints =>
        {
            endpoints.MapControllers();
        });
        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            c.SwaggerEndpoint("/swagger/v1/swagger.json", "ElectraArt API Version 1.5");
        });
    }
}
