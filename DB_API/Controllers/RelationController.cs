using Microsoft.AspNetCore.Mvc;
using ElectraArt_API.Services;

namespace ElectraArt_API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RelationController : ControllerBase
    {
        /// <summary>
        /// Controller for handling node relation data.
        /// </summary>
        private readonly GlobalRelation _globalRelationSVC;
        public RelationController(GlobalRelation globalRelation)
        {
            _globalRelationSVC = globalRelation;
        }

        /// <summary>
        /// Create a relation between user and art.
        /// </summary>
        /// <param name="usr_id">user id of the user</param>
        /// <param name="art_id">art id of the art</param>
        /// <param name="creationDate">creation date of the art</param>
        /// <param name="creationGuild">creation guild id of the art</param>
        [HttpPut]
        [Route("join/{usr_id}/{art_id}")]
        public async Task<IActionResult> CreateRelationToArt(long usr_id, long art_id, long creationDate, long creationGuild)
        {
            var v_usr_id = usr_id;
            var v_art_id = art_id;
            var v_creationDate = creationDate;
            var v_creationGuild = creationGuild;
            var result = await _globalRelationSVC.userGenArt(v_usr_id, v_art_id, v_creationDate, v_creationGuild);
            return Ok(result);
        }
    }
}