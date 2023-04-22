# Build image
FROM mcr.microsoft.com/dotnet/sdk:7.0-alpine AS build
WORKDIR /source

COPY ./*.csproj .
RUN dotnet restore --use-current-runtime

COPY . .
RUN dotnet publish -c Release -o /app --use-current-runtime --self-contained false --no-restore

# Deploy image
FROM mcr.microsoft.com/dotnet/aspnet:7.0-alpine
WORKDIR /app
COPY --from=build /app .

ENTRYPOINT ["/app/ElectraArt-API"]