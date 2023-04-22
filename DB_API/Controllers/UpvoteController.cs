using Microsoft.AspNetCore.Mvc;
using ElectraArt_API.Services;

namespace ElectraArt_API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    
    public class UpvoteController : ControllerBase
    {
        /// <summary>
        /// Controller for handling upvote data.
        /// </summary>
        private readonly GlobalUpvoteManger _globalUpvoteSVC;
        public UpvoteController(GlobalUpvoteManger globalUpvote)
        {
            _globalUpvoteSVC = globalUpvote;
        }

        /// <summary>
        /// Create a upvote between user and art.
        /// </summary>
        /// <param name="usr_id">user id of the user</param>
        /// <param name="username">username of the member</param>
        /// <param name="art_id">art id of the art</param>
        /// <param name="upvoteGuild">upvote guild id of the art</param>
        [HttpPut]
        [Route("{usr_id}/{art_id}")]
        public async Task<IActionResult> CreateUpvoteToArt(long usr_id, string username, long art_id, long upvoteGuild)
        {
            var v_usr_id = usr_id;
            var v_username = username;
            var v_art_id = art_id;
            var v_upvoteGuild = upvoteGuild;
            var result = await _globalUpvoteSVC.giveArtUpvote(v_usr_id, v_username, v_art_id, v_upvoteGuild);
            return Ok(result);
        }
    }
}
