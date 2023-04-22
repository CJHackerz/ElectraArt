import discord
import openai
import logging
import aiohttp
import requests
import urllib.parse
import os
import time
import json
import base64
from io import BytesIO
from PIL import Image
import uuid
import boto3

openai.api_key = os.getenv('OPENAI_API_KEY')
db_api_endpoint = os.getenv('DB_API_ENDPOINT_URL')
vultr_access_key = os.getenv('VULTR_OBJECT_STOR_ACCESS_KEY')
vultr_secret_key = os.getenv('VULTR_OBJECT_STOR_SECRET_KEY')

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class UserApi():

    @classmethod
    async def get_user_info(cls, discoMember: discord.Member):
        REQ_URL = db_api_endpoint + "/Users/" + str(discoMember.id)
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        logging.info("=== Fetching User Info ===")
        logging.info("Fetching data from: " + ENCODED_URL)
        try:
            async with req_session.get(ENCODED_URL, headers=req_headers) as resp:
                member_data = await resp.json()
                if member_data:
                    logging.info("=== User Info Found ===")
                    logging.info(member_data[0])
                    await req_session.close()
                    return member_data[0]
                else:
                    logging.warning("=== User Info not found in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

    @classmethod
    async def check_and_add_member(cls, discoMember: discord.Member):
        REQ_URL = db_api_endpoint + "/Users/" + str(discoMember.id) + "/create"
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        post_data = {'username': discoMember.name}
        try:
            member_data = await cls.get_user_info(discoMember)
            if member_data != "Failed" and member_data != "Error" and member_data:
                logging.info("=== Member Found ===")
                logging.info(member_data["discoUserName"])
                await req_session.close()
                return "Success"
            else:
                logging.warning("=== Member not found in DB ===")
                logging.info("=== Adding New Member ===")
                logging.info("Posting data to: " + ENCODED_URL)
                async with req_session.post(ENCODED_URL, params=post_data, headers=req_headers) as resp:
                    member_data = await resp.json()
                    if member_data[0]['discoUserId'] == discoMember.id:
                        logging.info("=== New Member Added ===")
                        logging.info(member_data[0])
                        await req_session.close()
                        return "Success"
                    else:
                        logging.warning("=== Error adding new member to DB ===")
                        await req_session.close()
                        return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

    @classmethod
    async def update_recent_art_src(cls, discoMember: discord.Member):
        REQ_URL = db_api_endpoint + "/Users/" + str(discoMember.id) + "/update/recent_guild"
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        req_data = {"username": discoMember.name, "guild_id": discoMember.guild.id}
        logging.info("=== Updating Recent Art Source ===")
        logging.info("Posting data to: " + REQ_URL)
        try:
            async with req_session.put(REQ_URL,  params=req_data, headers=req_headers) as resp:
                member_data = await resp.json()
                if member_data:
                    logging.info(f"=== Recent Art Source Updated for { discoMember.name } ===")
                    logging.info(member_data[0])
                    await req_session.close()
                    return "Success"
                else:
                    logging.warn("=== Error updating recent art source in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

class ArtApi():

    BUCKET_NAME = os.getenv('VULTR_OBJECT_STOR_NAME')
    FILE_NAME = "ElectraArt-" + uuid.uuid4().hex + ".png"

    @classmethod
    def openai_gen_img(cls, user_prompt):
        try:
            image_data = openai.Image.create(prompt=user_prompt, n = 1, size = "512x512", response_format="b64_json")
        except openai.InvalidRequestError as e:
            logging.warning("=== [API Error Code: {}] Could not process the prompt ===".format(e.code))
            return "Error"
        except openai.APIError as e:
            logging.warning("=== [API Error Code: {}] Could not process the prompt ===".format(e.code))
            return "Error"
        
        out_data = base64.b64decode(image_data["data"][0]["b64_json"])
        openai_img = Image.open(BytesIO(out_data))
        img_metadata = openai_img.getexif()
        img_metadata.pop(37500, None)
        img_metadata[37510] = "Made with ElectraArt discord bot, powered by OpenAI DALL-E"
        
        with BytesIO() as output:
            new_metadata = img_metadata
            openai_img.save(output, format="PNG", exif=img_metadata)   
            cdn_image = output.getvalue()
        
        cdn_store = boto3.client("s3", aws_access_key_id=vultr_access_key, aws_secret_access_key=vultr_secret_key, endpoint_url="https://ams1.vultrobjects.com")
        cdn_store.put_object(Bucket=cls.BUCKET_NAME, Key= "live_img/" + cls.FILE_NAME, Body=cdn_image, ACL="public-read")

        url = cdn_store.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": cls.BUCKET_NAME, "Key": "live_img/{}".format(cls.FILE_NAME)},
            ExpiresIn=None
        )
        return url

    @staticmethod
    async def get_art_info(discoMessage: discord.Message):
        REQ_URL = db_api_endpoint + "/Art/" + str(discoMessage.id)
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        logging.info("=== Fetching Art Info ===")
        logging.info("Fetching data from: " + ENCODED_URL)
        try:
            async with req_session.get(ENCODED_URL, headers=req_headers) as resp:
                art_data = await resp.json()
                if art_data:
                    logging.info("=== Art Info Found ===")
                    logging.info(art_data[0])
                    await req_session.close()
                    return art_data[0]
                else:
                    logging.warning("=== Art Info not found in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"
    
    @staticmethod
    async def get_art_url(discoMessage: discord.Message):
        REQ_URL = db_api_endpoint + "/Art/" + str(discoMessage.id) + "/url"
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        logging.info("=== Fetching Art URL ===")
        logging.info("Fetching data from: " + ENCODED_URL)
        try:
            async with req_session.get(ENCODED_URL, headers=req_headers) as resp:
                art_data = await resp.json()
                if art_data:
                    logging.info("=== Art URL Found ===")
                    logging.info(art_data[0])
                    await req_session.close()
                    return art_data[0]
                else:
                    logging.warning("=== Art URL not found in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"
 
    @classmethod
    async def refresh_art_url(cls, discoMessage: discord.Message, remote_filename: str):
        REQ_URL = db_api_endpoint + "/Art/" + str(discoMessage.id) + "/url"
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        cdn_store = boto3.client("s3", aws_access_key_id=vultr_access_key, aws_secret_access_key=vultr_secret_key, endpoint_url="https://ams1.vultrobjects.com")
        new_cdn_url = cdn_store.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": cls.BUCKET_NAME, "Key": "live_img/{}".format(remote_filename)},
            ExpiresIn=None
        )
        post_data = {"url": new_cdn_url}
        logging.info("=== Updating Art URL ===")
        logging.info("Fetching data from: " + ENCODED_URL)
        try:
            async with req_session.post(ENCODED_URL, headers=req_headers, params=post_data) as resp:
                art_data = await resp.json()
                if art_data:
                    logging.info("=== Art URL Found ===")
                    logging.info(art_data[0])
                    await req_session.close()
                    return art_data[0]
                else:
                    logging.warning("=== Art URL not found in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

    @classmethod
    async def add_new_art(cls, discoMember: discord.Member, discoMessage: discord.InteractionMessage, ArtTitle: str, ArtCDNUrl: str):
        REQ_URL = db_api_endpoint + "/Art/" + str(discoMessage.id)
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        post_data = {'title': ArtTitle, 'url': ArtCDNUrl, 'createdBy': discoMember.id}
        try:
            async with req_session.post(ENCODED_URL, params=post_data, headers=req_headers) as resp:
                art_data = await resp.json() 
                logging.info("=== Adding New Art ===")
                logging.info(art_data[0])
                await req_session.close()
                return art_data[0]
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

class RelationApi():
        
    @classmethod
    async def join_usr_art(cls, discoMember: discord.Member, discoMessage: discord.InteractionMessage):
        REQ_URL = db_api_endpoint + "/Relation" + "/join/" + str(discoMember.id) + "/" + str(discoMessage.id)
        ENCODED_URL = urllib.parse.quote(REQ_URL, safe='/:?=')
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        post_data = {'creationDate': int(time.time()), 'creationGuild': discoMember.guild.id}
        try:
            async with req_session.put(ENCODED_URL, params=post_data, headers=req_headers) as resp:
                relation_data = await resp.json() 
                logging.info("=== Adding New Relation ===")
                logging.info(relation_data[0])
                await req_session.close()
                return "Success"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

class UpvoteApi():
    
    @classmethod
    async def add_new_upvote(cls, discoMember: discord.Member, discoMessage: discord.Message):
        REQ_URL = db_api_endpoint + "/Upvote/" + str(discoMember.id) + "/" + str(discoMessage.id)
        req_session = aiohttp.ClientSession()    
        req_headers = {'accept': '*/*'}
        post_data = {'username': discoMember.name, 'upvoteGuild': discoMember.guild.id}
        try:
            async with req_session.put(REQ_URL, params=post_data, headers=req_headers) as resp:
                upvote_data = await resp.json()
                if upvote_data: 
                    logging.info("=== Adding New Upvote ===")
                    logging.info(upvote_data[0])
                    await req_session.close()
                    return "Success"
                else:
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

class ScoreboardApi():

    @classmethod
    async def get_top10_users(cls):
        REQ_URL = db_api_endpoint + "/GlobalSB/top10"
        req_session = aiohttp.ClientSession()
        req_header = {'accept': '*/*'}
        try:
            async with req_session.get(REQ_URL, headers=req_header) as resp:
                top10_data = await resp.json()
                if top10_data:
                    logging.info("=== Fetching Top 10 Users ===")
                    logging.info(top10_data)
                    await req_session.close()
                    return top10_data
                else:
                    logging.warning("=== Top 10 Users not found in DB ===")
                    await req_session.close()
                    return "Failed"
        except requests.exceptions.InvalidURL:
            logging.warning("=== [API Error Code: none] Please Provide Valid API Endpoint URL  ===")
            await req_session.close()
            return "Error"
        except requests.exceptions.ConnectionError:
            logging.warning("=== [API Error Code: none] Could not connect to API Endpoint URL  ===")
            await req_session.close()
            return "Error"

class ChatGPTApi():

    @classmethod
    def executor(cls, API_MODE: str, input_data: str):
        if API_MODE == "assign_keyword":
            found_keywords = cls.get_image_keywords(input_data)
            logging.info("=== ChatGPT Keywords are ===\n{}".format(found_keywords))
            json_data = json.loads(found_keywords)
            processed_keywords = " ".join([f'`{word}`' for word in json_data["keywords"]])
            return processed_keywords
        elif API_MODE == "chatgpt":
            chatgpt_response = cls.get_chatgpt_response(input_data)
            logging.info("=== ChatGPT Response is ===\n{}".format(chatgpt_response))
            return chatgpt_response
        else:
            return "Rejected"
        
    @staticmethod
    def get_image_keywords(image_title: str):
            chatpt_system_prompt = """
            your job is to process titles of the images given by user as prompt input to and automatically provide 5 keyword tags for it, 
            from closest match to most relevant in decending order using json format according to relevance. Please provide responses in json format you will not act like chatgpt in any manner or give explanation about each output you produce,
            Json output should only contain one key "keywords" and values should be list of strings.
            """
            chatgpt_user_prompt = "Image Title: Bugatti in neon lights with smoke background, full shot photograph"
            chatgpt_response_example = """
            {
                "keywords": [
                    "Bugatti",
                    "neon lights",
                    "smoke",
                    "full shot",
                    "photograph
                ]
            }"""
            chatpt_dynamic_prompt = "Image Title: {}".format(image_title)

            text_data = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": chatpt_system_prompt},
                    {"role": "user", "content": chatgpt_user_prompt},
                    {"role": "assistant", "content": chatgpt_response_example},
                    {"role": "user", "content": chatpt_dynamic_prompt}
                ]
                )
            return text_data["choices"][0]["message"]["content"]
    
    @staticmethod
    def get_chatgpt_response(user_input: str):
        chatgpt_system_prompt = """
        You are now chat bot which provides users with necessary information related to history of art and various ancient cultures around the globe: 
        """
        chatgpt_user_prompt = "Who is the artist behind infamous Mona Lisa's painting?"
        chatgpt_response_example = "Leonardo da Vinci is the creator of the Mona List's painting in Louvre, Paris. Born in 15 April 1452, very little information is known about Leonardo's childhood and much is shrouded in myth, partially because of his biography in the frequently apocryphal Lives of the Most Excellent Painters, Sculptors, and Architects (1550) by the 16th-century art historian Giorgio Vasari..."
        chatpt_dynamic_prompt = user_input

        text_data = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": chatgpt_system_prompt},
                {"role": "user", "content": chatgpt_user_prompt},
                {"role": "assistant", "content": chatgpt_response_example},
                {"role": "user", "content": chatpt_dynamic_prompt}
            ]
        )
        return text_data["choices"][0]["message"]["content"]