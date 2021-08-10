from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from fuzzywuzzy import process

import discord
import os
import json
import requests

from discord.ext.commands import Bot
from re import sub

description = "WoW Search"
bot_character = "wow-character!"
bot_guild = "wow-guild!"
bot_affix = "wow-affix!"
bot_auction = "wow-auction!"
bot_help = "wow-help!"
set_realm = "wow-realm!"
discord_token = os.environ.get("DISCORD_TOKEN")
wow_api_client_id = os.environ.get("WOW_API_CLIENT_ID")
wow_api_client_secret = os.environ.get("WOW_API_CLIENT_SECRET")
Client = discord.Client()
client = Bot(command_prefix=bot_character, description=description)


@client.event
async def on_message(message):
    if message.content.startswith(bot_character):
        data = {'grant_type': 'client_credentials'}
        token_auth = requests.post('https://eu.battle.net/oauth/token', data=data,
                                   auth=(wow_api_client_id, wow_api_client_secret))
        token_auth = token_auth.json()
        wow_api_key = token_auth["access_token"]

        player_name = message.content.replace(bot_character, "")
        player_name = sub(r"/.*", "", player_name)
        realm = sub(".*/", "", message.content)

        url = "https://eu.api.blizzard.com/wow/character/{}/{}?" \
              "locale=fr_FR&access_token={}&fields=items%2Cprogression%2Cachievements%2Cpvp" \
            .format(realm, player_name, wow_api_key)
        header = {"Accept": "application/json"}

        resp = requests.get(url, headers=header)
        player_result = resp.json()

        battle_group = player_result["battlegroup"]
        average_item_level = player_result["items"]["averageItemLevel"]
        average_item_level_equipped = player_result["items"]["averageItemLevelEquipped"]

        # ======================================================================================================================

        realm_battlenet = str(realm)
        realm_battlenet = realm_battlenet.replace("'", "")
        realm_battlenet = realm_battlenet.replace("-", "")
        armory_link = "#Armory_link : ```https://worldofwarcraft.com/fr-fr/character/{}/{}".format(realm_battlenet,
                                                                                                   player_name)

        # ======================================================================================================================

        stat_arena = "\n#Arena_rating :\n"
        pvp_modes = ["ARENA_BRACKET_2v2_SKIRMISH", "ARENA_BRACKET_2v2", "ARENA_BRACKET_3v3", "ARENA_BRACKET_RBG"]
        for pvp_mode in pvp_modes:
            rank_name = player_result["pvp"]["brackets"][pvp_mode]["slug"]
            rank = player_result["pvp"]["brackets"][pvp_mode]["rating"]
            stat_arena += "{} : '{}'    ".format(rank_name, rank)

        # ======================================================================================================================

        raids = ["Uldir", "Bataille de Dazar’alor"]
        stat_raid = "\n#Raids_progress : \n"
        kill_difficulties = "normalKills", "heroicKills", "mythicKills"

        for raid in raids:
            stat_raid = stat_raid + raid + "  :  "

            for i in range(len(player_result["progression"]["raids"])):
                if player_result["progression"]["raids"][i]["name"] == raid:

                    for kill_difficulty in kill_difficulties:
                        kill_count = 0
                        for j in range(len(player_result["progression"]["raids"][i]["bosses"])):
                            if player_result["progression"]["raids"][i]["bosses"][j][kill_difficulty] > 0:
                                kill_count += 1

                        stat_raid += "'{}/{}' {}    ".format(str(kill_count), str(len(
                            player_result["progression"]["raids"][i]["bosses"])), kill_difficulty)
            stat_raid += "\n"

        # ======================================================================================================================
        """
        mythic_indexs = 33097, 33098, 32028
        mythic_difficulties = "||  +5 = ", "  ||  +10 = ", "  ||  +15 = "
        count = 0
        mythic_result = {}
        mythic_progress = "\n#Mythic_progress : \n"
        for mythic_index in mythic_indexs:
            if mythic_index in player_result["achievements"]["criteria"]:
                index = player_result["achievements"]["criteria"].index(mythic_index)
                mythic_result[count] = str(player_result["achievements"]["criteriaQuantity"][index])
                count += 1
            else:
                mythic_result[count] = "0"
                count += 1
        count = 0
        for mythic_difficulty in mythic_difficulties:
            mythic_progress = mythic_progress + mythic_difficulty + mythic_result[count]
            count += 1
        """
        # ======================================================================================================================

        url = "https://raider.io/api/v1/characters/profile?region=EU&realm={}&name={}&fields=mythic_plus_scores" \
            .format(realm, player_name)

        mythic_score = requests.get(url).json()
        mythic_specializations = "all", "dps", "healer", "tank"
        mythic_specializations_prints = "All = ", "    DPS = ", "    Heal = ", "    Tank = "
        mythic_score_print = "\n#Mythic_Score : \n"
        count = 0
        score = {}

        for mythic_specialization in mythic_specializations:
            score[count] = str(mythic_score["mythic_plus_scores"][mythic_specialization])
            count += 1
        """
        else:
            mythic_result[count] = "0"
            count += 1
        """
        count = 0

        for mythic_specializations_print in mythic_specializations_prints:
            mythic_score_print += "{}'{}'".format(mythic_specializations_print, score[count])
            count += 1

        # ======================================================================================================================

        await message.channel.send("```css\n" + "#Player_name = " + str(player_name) +
                                   "\n#Realm = " + str(realm) +
                                   "\n#Battlegroup = " + str(battle_group) + "\n\n" +
                                   armory_link + "\n```css" + "\n" +
                                   "#Equiped_ilvl = " + str(average_item_level_equipped) +
                                   "\n#Average_ilvl = " + str(average_item_level) + "\n" +
                                   stat_arena + "\n" +
                                   mythic_score_print + "\n" +
                                   stat_raid + "```")

    # ======================================================================================================================

    elif message.content.startswith(bot_guild):
        guild_name = message.content.replace(bot_guild, "")
        guild_name = sub(r"/.*", "", guild_name)
        realm = sub(".*/", '', message.content)
        url = "https://raider.io/api/v1/guilds/profile?region=EU&realm=" + \
              realm + "&name=" + guild_name + "&fields=raid_progression%2Craid_rankings"
        resp = requests.get(url)
        guild_result = resp.json()

        raids = "battle-of-dazaralor", "uldir"
        rank_raid = ""
        prog_raid = ""

        for raid in raids:
            rank_raid = rank_raid + raid + " :\n#Normal\n #World = " + str(
                guild_result["raid_rankings"][raid]["normal"]["world"]) + "; #Region = " + str(
                guild_result["raid_rankings"][raid]["normal"]["region"]) + "; #Realm = " + str(
                guild_result["raid_rankings"][raid]["normal"]["realm"]) + "\n#Heroic\n #World = " + str(
                guild_result["raid_rankings"][raid]["heroic"]["world"]) + "; #Region = " + str(
                guild_result["raid_rankings"][raid]["heroic"]["region"]) + "; #Realm = " + str(
                guild_result["raid_rankings"][raid]["heroic"]["realm"]) + "\n#Mythic\n #World = " + str(
                guild_result["raid_rankings"][raid]["mythic"]["world"]) + "; #Region = " + str(
                guild_result["raid_rankings"][raid]["mythic"]["region"]) + "; #Realm = " + str(
                guild_result["raid_rankings"][raid]["mythic"]["realm"]) + "\n\n"

        for raid in raids:
            prog_raid = prog_raid + raid + "\n #Progression = " + str(
                guild_result["raid_progression"][raid]["summary"]) + "\n"

        await message.channel.send("```css" + "\n" + rank_raid + "\n" + prog_raid + "```")

    elif message.content.startswith(bot_affix):
        report_affixes = ""
        url = "https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en"
        week_affixes = requests.get(url).json()

        for affix_detail in week_affixes["affix_details"]:
            report_affixes += ("#" + affix_detail["name"] + "\n" + affix_detail["description"] + "\n\n")

        await message.channel.send("```css\n" + report_affixes + "\n```")

    elif message.content.startswith(bot_help):
        help_message = "Find a WoW character : wow-character!character_name/realm_name\n\n" \
                       "Find a WoW guild : wow-guild!guild_name/realm_name\n\n" \
                       "Find a WoW price : wow-auction!item_name\n\n" \
                       "Dash and space can be included in the realm_name and guild_name.\n\n" \
                       "If you want to participate or to report any problem, please go to " \
                       "https://github.com/Krazoc/discord_bot/blob/master/wow_search/wow_search.py"

        await message.channel.send(help_message)

    elif message.content.startswith(bot_auction):
        data = {'grant_type': 'client_credentials'}
        token_auth = requests.post('https://eu.battle.net/oauth/token', data=data,
                                   auth=(wow_api_client_id, wow_api_client_secret))

        recap = ""
        token_auth = token_auth.json()
        wow_api_key = token_auth["access_token"]

        if os.path.isfile('active_realm_info.json'):
            json_file = open('active_realm_info.json')
            connected_realm_detail = json.load(json_file)

            item_search = message.content.replace(bot_auction, "")

            if "'" in item_search:
                item_search = item_search.replace("'", "’")
                item_search_update = item_search.replace(" ", "&")

            else:
                item_search = '{}'.format(item_search)
                item_search_update = item_search.replace(" ", "&")

            url = "https://eu.api.blizzard.com/data/wow/search/item?" \
                  "namespace=static-eu&locale=fr_FR&name.fr_FR={}&orderby=level&_page=1&_pageSize=1000&" \
                  "access_token={}".format(item_search_update, wow_api_key)
            header = {"Accept": "application/json"}

            resp = requests.get(url, headers=header)
            item_results = resp.json()
            choices = []

            for item in item_results["results"]:
                choices.append(item["data"]["name"]["fr_FR"])
            result = process.extract(item_search, choices, limit=1)
            result_text = result[0][0]
            print(result_text)
            result_pourcentage = result[0][-1]
            print(result_pourcentage)

            item_found = False
            for item in item_results["results"]:
                if item["data"]["name"]["fr_FR"] == result_text and result_pourcentage >= 90:
                    item_found = True
                    print(item["data"]["name"]["fr_FR"])
                    recap += item["data"]["name"]["fr_FR"] + "\n"
                    print(item["data"]["media"]["id"])

                    url = "https://eu.api.blizzard.com/data/wow/connected-realm/{}/auctions" \
                          "?namespace=dynamic-eu&locale=fr_FR&access_token={}"\
                        .format(connected_realm_detail["realm"]["connected_realms_id"], wow_api_key)
                    header = {"Accept": "application/json"}

                    resp = requests.get(url, headers=header)
                    auction_results = resp.json()
                    price = 99999999999999999
                    price_dict = []
                    gold = ""
                    for auction in auction_results["auctions"]:
                        if auction["item"]["id"] == item["data"]["media"]["id"]:
                            if "unit_price" in auction.keys():
                                if auction["unit_price"] < price:
                                    price = auction["unit_price"]
                            if "buyout" in auction.keys():
                                if auction["buyout"] < price:
                                    price = auction["buyout"]
                    for digit in str(price):
                        price_dict.append(digit)
                    copper = "{}{}".format(price_dict[-2], price_dict[-1])
                    price_dict.pop(-1)
                    price_dict.pop(-1)
                    silver = "{}{}".format(price_dict[-2], price_dict[-1])
                    price_dict.pop(-1)
                    price_dict.pop(-1)
                    for gold_digit in price_dict:
                        gold += gold_digit
                    print("{} po, {} pa, {} pc".format(gold, silver, copper))
                    recap += "{} po, {} pa, {} pc".format(gold, silver, copper)
                elif item_found is False:
                    recap = "item not found"
            await message.channel.send("```css\n" + recap + "\n```")
        else:
            await message.channel.send("```css\n No server set, please set one\n```")

    elif message.content.startswith(set_realm):
        realm_search = message.content.replace(set_realm, "")

        connected_realm_detail = {}

        if os.path.isfile('connected_realm_index.json'):
            json_file = open('connected_realm_index.json')
            connected_realm_detail = json.load(json_file)
            file_exist = True

        else:
            file_exist = False
        if file_exist is False or "last_update" not in connected_realm_detail or datetime.today() > (
                parse(connected_realm_detail["last_update"]) + relativedelta(days=+7)):
            connected_realm_detail = {"last_update": "{}".format(datetime.today()), "connected_realms": []}
            data = {'grant_type': 'client_credentials'}
            token_auth = requests.post('https://eu.battle.net/oauth/token', data=data,
                                       auth=(wow_api_client_id, wow_api_client_secret))
            token_auth = token_auth.json()
            wow_api_key = token_auth["access_token"]

            url = "https://eu.api.blizzard.com/data/wow/connected-realm/index" \
                  "?namespace=dynamic-eu&locale=fr_FR&access_token={}".format(wow_api_key)

            header = {"Accept": "application/json"}

            resp = requests.get(url, headers=header)
            connected_realms_index = resp.json()

            for connected_realm in connected_realms_index["connected_realms"]:
                connected_realm_id = connected_realm["href"].replace(
                    "https://eu.api.blizzard.com/data/wow/connected-realm/", "") \
                    .replace("?namespace=dynamic-eu", "")
                url = "https://eu.api.blizzard.com/data/wow/connected-realm/{}" \
                      "?namespace=dynamic-eu&locale=fr_FR&access_token={}".format(connected_realm_id, wow_api_key)

                header = {"Accept": "application/json"}

                resp = requests.get(url, headers=header)
                connected_realm_detail["connected_realms"].append(resp.json())
            with open('connected_realm_index.json', 'w') as connected_realms_index_file:
                json.dump(connected_realm_detail, connected_realms_index_file)
        server_set = False
        for realms in connected_realm_detail["connected_realms"]:
            for realm in realms["realms"]:
                if realm["name"] == realm_search:
                    data = {"realm": {'name': realm["name"],
                                      'slug': realm["slug"],
                                      'id': "",
                                      'connected_realms_id': realms["id"]}}
                    recap = "Server set"
                    with open('active_realm_info.json', 'w') as active_realm_info_file:
                        json.dump(data, active_realm_info_file)
                    server_set = True
                    break
            if realm["name"] == realm_search:
                break

        if server_set is False:
            recap = "Server not found"

        await message.channel.send("```css\n" + recap + "\n```")

client.run(discord_token)
