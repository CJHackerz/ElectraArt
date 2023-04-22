#pragma warning disable 1591

namespace ElectraArt_API.Exceptions
{
    public class ValidationException : Exception
    {
        public readonly int Code = 422;
        public string Details { get; init; }

        public ValidationException(string message, string details)
            : base(message)
        {
            Details = details;
        }
    }
}