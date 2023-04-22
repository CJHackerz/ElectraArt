#pragma warning disable 1591

namespace ElectraArt_API.Exceptions
{
    public class NotFoundException : Exception
    {
        public NotFoundException(string message) : base(message)
        {
        }

        public readonly int Code = 404;
    }
}