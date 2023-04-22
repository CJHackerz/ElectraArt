using Microsoft.AspNetCore.Mvc;
using ElectraArt_API.Services;

namespace ElectraArt_API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    
    public class UsersController : ControllerBase
    {
        /// <summary>
        /// Controller for handling User data.
        /// </summary>
        private readonly GlobalUser _sbMemberUpdate;
        public UsersController(GlobalUser sbMemberUpdate)
        {
            _sbMemberUpdate = sbMemberUpdate;
        }

        /// <summary>
        /// Get User Data using Discord ID.
        /// </summary>
        /// </param name="id">discord user id of the member</param>
        /// <returns>Scoreboard User Data</returns>
        [Route("{id}")]
        [HttpGet]
        public async Task<IActionResult> GetUserById(long id)
        {
            var v_id = id;
            var user = await _sbMemberUpdate.findMember(v_id);
            return Ok(user);
        }
        /// <summary>
        /// Get recent Guild ID where member created art.
        /// </summary>
        /// </param name="id">discord user id of the member</param>
        /// <returns>Recent guild id</returns>
        [Route("{id}/recent_guild_id")]
        [HttpGet]
        public async Task<IActionResult> GetRecentGuild(long id)
        {
            var v_id = id;
            var user = await _sbMemberUpdate.getRecentGuild(v_id);
            return Ok(user);
        }
        /// <summary>
        /// Create a new User Data using Discord ID and Discord Username.
        /// </summary>
        /// </param name="id">discord user id of the member</param>
        /// </param name="username">discord username of the member</param>
        /// <returns>User Data Update</returns>

        [Route("{id}/create")]
        [HttpPost]
        public async Task<IActionResult> CreateUser(long id, string username)
        {
            var v_id = id;
            var v_username = $"{username}";
            var user = await _sbMemberUpdate.newMember(v_id, v_username);
            return Created($"api/users/{v_id}/{v_username}", user);
        }

        /// <summary>
        /// Update recent guild id in User data using Discord ID and Discord Username.
        /// </summary>
        /// </param name="id">discord user id of the member</param>
        /// </param name="username">discord username of the member</param>
        /// </param name="guild_id">Guild ID of discord server where member recently create the art</param>

        /// <returns>User Data Update</returns>

        [Route("{id}/update/recent_guild")]
        [HttpPut]
        public async Task<IActionResult> UpdateRecentGuild(long id, string username, long guild_id)
        {
            var v_id = id;
            var v_username = $"{username}";
            var user = await _sbMemberUpdate.updateMember(v_id, v_username, guild_id, 0);
            return Created($"api/users/{v_id}/{v_username}/{guild_id}", user);
        }    

        /// <summary>
        /// Update upvote count in User data using Discord ID and Discord Username.
        /// </summary>
        /// </param name="id">discord user id of the member</param>
        /// </param name="username">discord username of the member</param>
        /// </param name="upvotes">Upvote count of the member</param>
        [Route("{id}/update")]
        [HttpPost]
        public async Task<IActionResult> UpdateUVCount(long id, string username, int upvotes)
        {
            var v_id = id;
            var v_username = $"{username}";
            var v_upvotes = upvotes;
            var user = await _sbMemberUpdate.updateMember(v_id, v_username, 0, v_upvotes);
            return Created($"api/users/{v_id}/{v_username}/upvotes", user);
        }    
    }
}