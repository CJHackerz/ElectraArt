# ElectraArt
Opensource discord bot which generates images using DALL-E from OpenAI

![](./Docs/project-logo.png)

## What is this?
It is discord bot written in Python, C# .NET API and Neo4j graph database. Using your API Token from DALL-E it will generate images and post it on same channel where you ran `/genimage` command and provided a small description about the image as text input parameter. My code example includes how to build and host this behind docker-compose using remote container registry (On Dockerhub or GitHub or GitLab you can create private repo and enable registry for it). Source code also includes a gitlab pipeline example, where in project settings you have to set environmental variables to provide crendeitals and other required information.
Finally it utilizes docker in docker service on gitlab docker runner to deploy the bot under container environment.

## Features
* Image tags using simple prompt engineering and ChatGPT (makes your life easy to find images, using seach box of your discord channels with help of keywords)
* Upvote Button
* Download button (just easy way to get direct link to picture uploaded in CDN in our case I recommend vulture [use the code at the end to get 100$ credit for testing out one of the cost effective cloud platform])
* Configuration File to only allow bot run on specific servers and not to get huge bill!
* Helper command `/genhelp`
* Using chatgpt give information about ancient artists and famous cultures around the globe.

Graph DB View:
![](./Docs/Screenshots/Screenshot%20from%202023-04-22%2001-18-29.png)

Demmo shots from discord:
![](./Docs/Screenshots/Screenshot%20from%202023-04-22%2001-22-49.png)
![](./Docs/Screenshots/Screenshot%20from%202023-04-22%2001-23-27.png)

## Refferal Links

https://www.vultr.com/?ref=9367494-8H