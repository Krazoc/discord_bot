import discord
import os
import requests

from discord.ext.commands import Bot
from re import sub

description = "WoW Search"
bot_prefix = "wow-c!"
bot_prefix2 = "wow-g!"
bot_prefix3 = "wow-a!"
bot_prefix_help = "wow-help!"
bot_prefix_coincoin = "coincoin!"
discord_token = os.environ.get("DISCORD_TOKEN")
wow_api_client_id = os.environ.get("WOW_API_CLIENT_ID")
wow_api_client_secret = os.environ.get("WOW_API_CLIENT_SECRET")
Client = discord.Client()
client = Bot(command_prefix=bot_prefix, description=description)


@client.event
async def on_message(message):
    if message.content.startswith(bot_prefix):
        data = {'grant_type': 'client_credentials'}
        token_auth = requests.post('https://eu.battle.net/oauth/token', data=data,
                                   auth=(wow_api_client_id, wow_api_client_secret))
        token_auth = token_auth.json()
        wow_api_key = token_auth["access_token"]

        player_name = message.content.replace(bot_prefix, "")
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

        await client.send_message(message.channel, "```css\n" + "#Player_name = " + str(player_name) +
                                  "\n#Realm = " + str(realm) +
                                  "\n#Battlegroup = " + str(battle_group) + "\n\n" +
                                  armory_link + "\n```css" + "\n" +
                                  "#Equiped_ilvl = " + str(average_item_level_equipped) +
                                  "\n#Average_ilvl = " + str(average_item_level) + "\n" +
                                  stat_arena + "\n" +
                                  mythic_score_print + "\n" +
                                  stat_raid + "```")

    # ======================================================================================================================

    elif message.content.startswith(bot_prefix2):
        guild_name = message.content.replace(bot_prefix2, "")
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

        await client.send_message(message.channel, "```css" + "\n" + rank_raid + "\n" + prog_raid + "```")

    elif message.content.startswith(bot_prefix3):
        report_affixes = ""
        url = "https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en"
        week_affixes = requests.get(url).json()

        for affix_detail in week_affixes["affix_details"]:
            report_affixes += ("#" + affix_detail["name"] + "\n" + affix_detail["description"] + "\n\n")

        await client.send_message(message.channel, "```css\n" + report_affixes + "\n```")

    elif message.content.startswith(bot_prefix_help):
        help_message = "Find a WoW character : wow-c!character_name/realm_name\n\n" \
                       "Find a WoW guild : wow-g!guild_name/realm_name\n\n" \
                       "Dash and space can be included in the realm_name and guild_name.\n\n" \
                       "If you want to participate or to report any problem, please go to " \
                       "https://github.com/Krazoc/discord_bot/blob/master/wow_search/wow_search.py"

        await client.send_message(message.channel, help_message)

    elif message.content.startswith(bot_prefix_coincoin):
        url = "https://www.youtube.com/watch?v=FSoQNtU-MFA"
        await client.send_message(message.channel, url)


client.run(discord_token)
