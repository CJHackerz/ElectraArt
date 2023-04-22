using Microsoft.AspNetCore.Mvc;
using ElectraArt_API.Services;

namespace ElectraArt_API.Controllers
{
    [Route("api/[controller]/top10")]
    [ApiController]
    
    public class GlobalSBController : ControllerBase
    {
        /// <summary>
        /// Controller for fetching top 10 members from scoreboard.
        /// </summary>
        private readonly FetchGlobalSB _fetchGlobalSB;
        public GlobalSBController(FetchGlobalSB fetchGlobalSB)
        {
            _fetchGlobalSB = fetchGlobalSB;
        }

        /// <summary>
        /// Gets a list of top 10 members from scoreboard.
        /// </summary>
        /// <returns>Member List</returns>
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            var top10 = await _fetchGlobalSB.GlobalTop10();
            return Ok(top10);
        }
    }
}