using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using ElectraArt_API.Services;

namespace ElectraArt_API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    
    public class ArtController : ControllerBase
    {
        /// <summary>
        /// Controller for handling Art data.
        /// </summary>
        private readonly GlobalArt _GlobalArtSVC;
        public ArtController(GlobalArt fetchGlobalArt)
        {
            _GlobalArtSVC = fetchGlobalArt;
        }

        /// <summary>
        /// Get Art Data using Art ID.
        /// </summary>
        /// <param name="id">art id of the Art</param>
        [Route("{id}")]
        [HttpGet]
        public async Task<IActionResult> GetArtById(long id)
        {   var v_id = id;
            var selectedArt = await _GlobalArtSVC.findArt(v_id);
            return Ok(selectedArt);
        }

        /// <summary>
        /// Get Art title using Art ID.
        /// </summary>
        /// <param name="id">Tittle of the Art</param>
        [Route("{id}/title")]
        [HttpGet]
        public async Task<IActionResult> GetArtTitle(long id)
        {   var v_id = id;
            var selectedArtData = await _GlobalArtSVC.getArtTitle(v_id);
            return Ok(selectedArtData);
        }

        /// <summary>
        /// Get Art Creator using Art ID.
        /// </summary>
        /// <param name="id">Creator of the Art</param>
        [Route("{id}/createdBy")]
        [HttpGet]
        public async Task<IActionResult> GetArtCreator(long id)
        {   var v_id = id;
            var selectedArtData = await _GlobalArtSVC.getArtCreatedBy(v_id);
            return Ok(selectedArtData);
        }

        /// <summary>
        /// Get Art URL using Art ID.
        /// </summary>
        /// <param name="id">CDN URL of the Art</param>
        [Route("{id}/url")]
        [HttpGet]
        public async Task<IActionResult> GetArtUrl(long id)
        {   var v_id = id;
            var selectedArtData = await _GlobalArtSVC.getArtUrl(v_id);
            return Ok(selectedArtData);
        }

        /// <summary>
        /// Create a new Art Data using Art ID, Art Title, Art URL, and Art Creator.
        /// </summary>
        /// <param name="id">art id of the Art</param>
        [Route("{id}")]
        [HttpPost]
        public async Task<IActionResult> CreateArt(long id, string title, string url, long createdBy)
        {   var v_id = id;
            var v_title = title;
            var v_url = url;
            var v_createdBy = createdBy;
            var selectedArtData = await _GlobalArtSVC.newArt(v_id, v_title, v_url, v_createdBy);
            return Ok(selectedArtData);
        }

        /// <summary>
        /// Update Art URL using Art ID and New URL.
        /// </summary>
        /// <param name="id">art id of the Art</param>
        /// <param name="url">New CDN URL to be updated in DB</param>
        [Route("{id}/url")]
        [HttpPost]
        public async Task<IActionResult> updateArt_url(long id, string url)
        {   var v_id = id;
            var v_url = url;
            var selectedArtUrl = await _GlobalArtSVC.updateArtUrl(v_id, v_url);
            return Ok(selectedArtUrl);
        }
    }
}