import discord
from discord.ext.commands import Bot
import os
from zipfile import ZipFile
import requests
import re
import shutil

from text_helper import *

delete_after_upload = True
anonymize_nicknames = True

source_path = os.path.dirname(os.path.realpath(__file__))
build_path = os.path.join(source_path, "build")
if not os.path.exists(build_path):
    os.mkdir(build_path)

bot = Bot("!")


def read_token():
    with open("token.txt", "r") as file:
        return file.readlines()[0].strip()


token = read_token()


def get_all_file_paths(directory):  # for ZipFile
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths



image_formats = ["png", "jpg", "jpeg", "gif"]
first_names = ["William", "James", "Harper", "Mason", "Evelyn", "Ella", "Marie", "John", "George", "Oliver", "Jack",
               "Harry", "Jacob", "Charlie", "Thomas", "Oscar", "Connor", "Kyle", "Richard", "Amelia", "Olivia", "Emily",
               "Poppy", "Isabella", "Jessica", "Sophie", "Samantha", "Elizabeth", "Lauren", "Sarah", "Filip", "Abraham",
               "Stephan", "Madison", "Colton", "Cooper", "Myles", "Hope"]


def filter_string(string):
    return re.sub('[^a-zA-Z0-9 \n\.\-\_]', '', string).replace(" ", "-")


@bot.command()
async def backup_all(ctx):

    main_folder_name = "serverBackup_" + filter_string(ctx.guild.name)
    main_path = os.path.join(build_path, main_folder_name)
    print("Backup of: " + filter_string(ctx.guild.name) + " - Started...")
    if not os.path.exists(main_path):
        os.mkdir(main_path)

    for text_channel in ctx.guild.text_channels:

        if text_channel.category is not None:
            channel_name = filter_string(text_channel.category.name) + "_" + filter_string(text_channel.name)
        else:
            channel_name = filter_string(text_channel.name)


        channel_path = os.path.join(main_path, channel_name)
        if not os.path.exists(channel_path):
            os.mkdir(channel_path)


        markdown_name = filter_string(text_channel.name[0:20]) + ".md"
        file = open(os.path.join(channel_path, markdown_name), 'wb')

        header_text = "###" + text_channel.name + "\n\n"
        file.write((header_text).encode("utf-8"))

        async for message in text_channel.history(limit=10000, oldest_first=True):
            output_string = "\n"
            was_attachment = False

            if anonymize_nicknames:
                output_string += first_names[int(message.author.id) % len(first_names)] + ": "
            else:
                output_string += message.author.name + ": "

            for attachment in message.attachments:
                was_attachment = True
                attachment_file_name = str(attachment.id) + "_" + filter_string(attachment.filename)
                attachment_file_path = os.path.join(channel_path, attachment_file_name)
                await attachment.save(attachment_file_path)

                if any(attachment_file_name.lower().endswith(image_format) for image_format in image_formats):
                    output_string += "![" + attachment.filename + "](" + attachment_file_name + "?raw=true)\n\n"
                else:
                    output_string += "![" + attachment.filename + "](" + attachment_file_name + ")\n\n"

            if was_attachment:  ## If there's a picture, we want to also save the reactions to it
                if message.reactions:
                    output_string += "|"
                for reaction in message.reactions:
                    output_string += " "
                    if type(reaction.emoji) is type("string"):
                        output_string += reaction.emoji
                    else:
                        output_string += reaction.emoji.name
                    output_string += " - " + str(reaction.count) + " |"

            output_string += "\n\n"

            output_string += message.content
            output_string += "\n___"
            file.write((output_string).encode("utf-8"))

        file.close()

    print("Backup of: " + filter_string(ctx.guild.name) + " - Finished.")

    print("Zipping " + main_folder_name + ".zip - Started...")
    file_paths = get_all_file_paths(main_path)
    zip_name = main_folder_name + ".zip"
    zip_path = os.path.join(build_path, zip_name)
    length_of_build_path = len(build_path)
    with ZipFile(zip_path, "w") as zip_saved:
        for file in file_paths:
            zip_saved.write(file, file[length_of_build_path:])
    print("Zipping " + zip_name + " - Finished.")
    print("Uploading " + zip_name + " to Discord - Started...")
    try:
        await ctx.send(file=discord.File(zip_path))
        print("Uploading " + zip_name + " to Discord - Finished.")

    except discord.errors.HTTPException:
        print("Uploading " + zip_name + " to Discord - Finished with an ERROR!")
        print("Uploading " + zip_name + " to File.io - Started...")
        await ctx.send("File `" + zip_name + "` is too large for Discord.\nLink to File.io will be generated soon.")
        zip_file = open(zip_path, 'rb')
        files = {
            'file': (zip_name, zip_file),
        }
        response = requests.post('https://file.io/', files=files)
        result = response.json()
        zip_file.close()
        print("Uploading " + zip_name + " to File.io - Finished.")
        if result["success"]:
            await ctx.send("Download (single-use) `" + zip_name + "`: " + result["link"])
        else:
            await ctx.send(
                "There was an error during the upload. Error message: " + result["message"] + ".")

    if delete_after_upload:
        print("Deleting " + main_folder_name + " - Started...")
        try:
            shutil.rmtree(main_path)
            os.remove(zip_path)
            print("Deleting " + main_folder_name + " - Finished.")
        except OSError as e:
            print(e)



@bot.event
async def on_ready():
    print(create_line_of_chars("#") + "\tBot is now fully working.\n" + create_line_of_chars("#"))
    print("\tDisplaying logs: \n")


bot.run(token)