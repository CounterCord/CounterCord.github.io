#CounterCord BitcoinJake09 3/13/2022
class guildsList:
    def __init__(self, name, id):
        self.name = name
        self.id = str(id)
        self.members = []
        self.assets = []
    def appendMember(self, id):
        self.members.append(str(id))
    def setMembers(self, memList):
        self.members = memList
    def addAsset(self, a):
        self.assets.append(a)
    def delAsset(self, a):
        count = 0
        for asset in self.assets:
            if a == asset.name:
                self.assets.pop(count)
            count = count + 1

class user:
    def __init__(self, name, id, v):
        self.name = name
        self.id = str(id)
        self.isVerified = v
        self.address = ''
        self.verifiedAssets = []
    def verify(self, v):
        self.isVerified = v
    def setAddress(self, a):
        self.address = a
    def addAsset(self, a):
        self.verifiedAssets.append(a)
    def delAsset(self, a):
        self.verifiedAssets.remove(a)

class asset:
    def __init__(self, name):
        self.name = name
        self.block = 0
    def setBlock(self, b):
        self.block = b

class verification:
    def __init__(self, name, a, b):
        self.name = name
        self.alpha = a
        self.blockStart = b
        self.startTime = int(time.time())

import json
import discord
from dtoken import TOKEN, TOKEN2
from discord.ext import commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
import requests
from requests.auth import HTTPBasicAuth
from requests_html import AsyncHTMLSession
import asyncio
import time
import random, string
from os.path import exists
import codecs

testNet = False # change to False to run on mainnet | True for testnet

print("Application has started...")

if testNet:
    url = "http://api.counterparty.io:14000/api/"
    tokenWallet = 'mxcpccCQoZsN73dgf3qWr5pGUAwjaLgcGd'
    regToken = "XCPTEST"
    defaultToken = "XCPTEST.SUBASSET"
    fName = "testnetguilds.json"
    sleepTime = 60*1
    tok = TOKEN2
else:
    url = "http://api.counterparty.io:4000/api/"
    tokenWallet = '1XcPcCzwrXBhiiUBc1cbtii3HU7LWwPvY'
    regToken = "COUNTERCORD"
    defaultToken = "COUNTERCORD.CASH"
    fName = "guilds.json"
    sleepTime = 60*5
    tok = TOKEN

sleepTime = 60*1

ccSiteURL = "https://countercord.github.io/"
ccGithubURL = "https://github.com/CounterCord/CounterCord"

headers = {'content-type': 'application/json'}
auth = HTTPBasicAuth('rpc', 'rpc')


verificationList = []
unverified = []
verified = []
loadList = []
GUILDLIST = []
USERLIST = []
ASSETLIST = []

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
bot = discord.Client(intents=discord.Intents.all())

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
    print(f'Connected to {bot.user.name}!')
    await asyncio.create_task(loadGuilds(bot))
    asyncio.create_task(jsonSaver(bot))
    asyncio.create_task(assetManager())
    print(f'{bot.user.name} is Ready!')



async def loadGuilds(bot):
    # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
    guild_count = 0
    tempGuildIdList = []
    tempUsers = []
    tempMemberIdList = []
    tempMember = None
    tempGuildMemberIDs = []
    for gs in bot.guilds:
        for m in gs.members:
            tempGuildMemberIDs.append(str(m.id))
    if not exists('guilds.json'):
        await asyncio.create_task(createJsonFile())
    with open('guilds.json') as json_file:
        data = json.load(json_file)
        if data is not None:
            for gs in data['Guilds']:
                tempMems = []
                #print('Loaded Guild: ' + gs['Name'])
                #tempGuildIdList.append(gs['ID'])
                tempGuild = guildsList(gs['Name'], gs['ID'])
                for memID in gs['Members']:
                    if str(memID) in tempGuildMemberIDs:
                        tempMems.append(str(memID))
                tempGuild.setMembers(tempMems)
                for a in gs['Assets']:
                    tempGuild.addAsset(asset(a))
                if tempGuild.id not in tempGuildIdList:
                    tempGuildIdList.append(tempGuild.id)
                    GUILDLIST.append(tempGuild)



            for member in data['Members']:
                tempUsers = []
                memsIDs = str(member["ID"])
                if memsIDs in tempGuildMemberIDs:
                    if memsIDs not in tempMemberIdList:
                        tempMember = user(member['Name'], str(member['ID']), str(member['IsVerified']))
                        tempMember.setAddress(member['Address'])
                        for a in member['Assets']:
                            tempMember.addAsset(asset(a))
                        tempUsers.append(tempMember)
                        tempMemberIdList.append(memsIDs)
                        #print("tempMemberIdList: " + memsIDs)
                        USERLIST.append(tempMember)

            for assetl in data['Assets']:
                tempAssets = []
                aName = str(assetl["Name"])
                aBlock = assetl["Block"]
                if aName not in tempAssets:
                    tempAsset = asset(aName)
                    tempAsset.setBlock(aBlock)
                    ASSETLIST.append(tempAsset)


            #print('size ' + str(len(GUILDLIST)))

    for guild in bot.guilds:
        unverified = []
        for member in guild.members:
            if not member.bot:
                if str(member.id) not in tempMemberIdList:
                    tempMemberIdList.append(str(member.id))
                    tempMember = user(member.name, str(member.id), str(False))
                    unverified.append(str(member.id))
                    USERLIST.append(tempMember)

                    #print(
                    #    f'{bot.user.name} is connected to the following guild:\n'
                    #    f'(Guild: {guild.name} id: {guild.id})'
                    #)


        if str(guild.id) not in tempGuildIdList:
            tempGuild = guildsList(guild.name, guild.id)
            tempGuild.setMembers(unverified)
            GUILDLIST.append(tempGuild)
        guild_count = guild_count + 1


    #for tMemIds in tempMemberIdList:
    #    for guild in GUILDLIST:
    #        for member in guild.members:
    #            if member is tMemIds:
    #                USERLIST.append(member)
    #for member in USERLIST:
        #print('MemberTest - ' + member.name + ' Verified: ' + str(member.isVerified))
    #print('size ' + str(len(GUILDLIST)))

	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
    print(bot.user.name + " is in " + str(guild_count) + " servers!")
    print("Guild search finished...")

async def getMemberByID(id):
    u = None
    for m in USERLIST:
        if str(m.id) is str(id):
            return m
    return u

async def removeMemberByID(id):
    c = 0
    for m in USERLIST:
        if m.id is id:
            USERLIST.pop(c)
            return True
        c=c+1
    return False

async def getMemberAssetNameList(mem):
    l = []
    if len(mem.verifiedAssets) > 0:
        for a in mem.verifiedAssets:
            l.append(a.name)
    return l

async def getMemberAssetList(mem):
    l = []
    for a in mem.verifiedAssets:
        l.append(a)
    return l

async def getMemberAssetByName(mem, aName):
    for a in mem.verifiedAssets:
        if a.name == aName:
            return a
    return None

async def getAssetByName(n):
    r = None
    for a in ASSETLIST:
        if a.name is n:
            return a
    return r

async def getGuildByID(id):
    for g in bot.guilds:
        if str(g.id) == str(id):
            return g
    return None

async def userInGuildList(G,ID):
    tf = False
    for u in G.members:
        if str(u) is str(ID):
            return True
    return tf

async def memberNameCheck(ID):
    for g in bot.guilds:
        for m in g.members:
            if str(m.id) == str(ID):
                return m.name
    return False

async def saveJson(bot):
    #print('size ' + str(len(GUILDLIST)))
    with open(fName, 'r') as json_file:
        data = json.load(json_file)
    information = {"Guilds":[],"Members":[],"Assets":[]}
    for gs in GUILDLIST:
        g = await getGuildByID(gs.id)
        if g is not None:
            memList = []
            for member in g.members:
                if not member.bot:
                    memList.append(str(member.id))
            gjson = {
                "Name":g.name,
                "ID":str(g.id),
                "Members": [str(mid) for mid in memList],
                "Assets":[str(a.name) for a in gs.assets]}
            information["Guilds"].append(gjson)
    for member in USERLIST:
        mjson = {
            "Name": await memberNameCheck(member.id),
            "ID":str(member.id),
            "Address":member.address,
            "IsVerified":str(member.isVerified),
            "Assets":[str(a.name) for a in member.verifiedAssets]}
        information["Members"].append(mjson)
    for asset in ASSETLIST:
        ajson = {
            "Name":asset.name,
            "Block":asset.block}
        information["Assets"].append(ajson)
    with open(fName, 'w') as fp:
        json.dump(information, fp, indent=2)

async def jsonSaver(bot):
    while(True):
        #print('jsonSaver checking data...')
        await saveJson(bot)
        #print('jsonSaver waiting...')
        await asyncio.sleep(sleepTime)
# get last XCP/BTC block

async def assetManager():
    print("Asset Manager Started...")
    asyncio.create_task(assetDiscordRoleMonitor())
    asyncio.create_task(assetMemberRoleMonitor())
    asyncio.create_task(BTCRoleMonitor())
    asyncio.create_task(XcpBlockMonitor())

async def BTCRoleMonitor():
    print("BTC Role Monitor Started...")
    while(True):
        for mem in USERLIST:
            for gs in bot.guilds:
                for member in gs.members:
                    if str(member.id) == str(mem.id):
                        if not discord.utils.get(gs.roles,name="BTC-Verified"):
                            await gs.create_role(name="BTC-Verified")
                        if discord.utils.get(gs.roles,name="BTC-Verified"):
                            ar = discord.utils.get(gs.roles,name="BTC-Verified")
                            if str(mem.isVerified) == "True":
                                if ar not in member.roles:
                                    await member.add_roles(ar)
                            if str(mem.isVerified) == "False":
                                if ar in member.roles:
                                    await member.remove_roles(ar)

        await asyncio.sleep(sleepTime)


async def XcpBlockMonitor():
    print("XCP Block Monitor Started...")
    lastBlock = await getLastBlock()
    while lastBlock is None:
        lastBlock = await getLastBlock()
        await asyncio.sleep(sleepTime)
    tempBlock = lastBlock
    while(True):
        lastBlock = await getLastBlock()
        if lastBlock is not None:
            if (lastBlock > tempBlock):
                if (lastBlock >= tempBlock+2):
                    lastBlock = tempBlock+1
                print("XCP asset check")
                await checkAssetsFromBlock(lastBlock)
                tempBlock = lastBlock

        await asyncio.sleep(sleepTime)

async def assetDiscordRoleMonitor():
    print("Asset Discord Role Monitor Started...")
    while(True):
        lastBlock = await getLastBlock()
        while lastBlock is None:
            lastBlock = await getLastBlock()
            await asyncio.sleep(sleepTime)
        if lastBlock is not None:
            count = 0
            for a in ASSETLIST:
                if lastBlock > a.block:
                    print("Asset: "+str(a.name)+" Expired!")
                    for gs in bot.guilds:
                        if discord.utils.get(gs.roles, name=str(a.name)+"-Verified") is not None:
                            role_object = discord.utils.get(gs.roles, name=str(a.name)+"-Verified")
                            await role_object.delete()
                    for g in GUILDLIST:
                        for ga in g.assets:
                            if ga.name == str(a.name):
                                g.delAsset(str(a.name))
                    ASSETLIST.pop(count)
                count = count + 1
        await asyncio.sleep(sleepTime)

async def assetMemberRoleMonitor():
    print("Asset Member Role Monitor Started...")
    while(True):
        for g in GUILDLIST:
            hodlersList = []
            for assets in g.assets:
                hodlersList = await assetGetHolders(assets.name)
                await assetCheckHolders(assets.name, hodlersList)
                await assetCheckRoles(assets.name)
        await asyncio.sleep(sleepTime)

async def assetCheckHolders(assetName, ckList):
    for mem in USERLIST:
        tAssetList = await getMemberAssetNameList(mem)
        if assetName in tAssetList:
            if mem.address not in ckList:
                mem.delAsset(await getMemberAssetByName(mem, assetName))
        if assetName not in tAssetList:
            if mem.address:
                if ckList:
                    if mem.address in ckList:
                        mem.addAsset(asset(assetName))

async def assetCheckRoles(assetName):
    for mem in USERLIST:
        for gs in bot.guilds:
            for member in gs.members:
                if str(member.id) == str(mem.id):
                    if discord.utils.get(gs.roles,name=str(assetName)+"-Verified"):
                        ar = discord.utils.get(gs.roles,name=str(assetName)+"-Verified")
                        tempA = await getMemberAssetNameList(mem)
                        #print(mem.name + " tempA: " + str(tempA) + " ==? "+ assetName)
                        if (assetName not in tempA):
                            if ar in member.roles:
                                await member.remove_roles(ar)
                        if (assetName in tempA):
                            if ar not in member.roles:
                                await member.add_roles(ar)


async def assetGetHolders(assetName):
    hodlerList = []
    parms = {"asset":str(assetName)}
    payload = {"method": "get_holders","params": parms,"jsonrpc": "2.0","id": 0}
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    jsonData = json.loads(response.text)
    r=jsonData["result"]
    if r != []:
        for l in r:
            for k, v in l.items():
                if str(k)== "address":
                    hodlerList.append(str(v))
                    #print("k: " + str(k) + " v: " + str(v))
        return hodlerList
    else:
        return None
        #print("its NONE!")

async def getLastBlock():
    try:
        payload = {"method": "get_running_info","params": {},"jsonrpc": "2.0","id": 0}
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        jsonData = json.loads(response.text)
        r=jsonData["result"]
        strReturn = None;
        for key, value in r.items():
            if (str(key) == "last_block"):
                jD = value
                if jD is not None:
                    for k, v in jD.items():
                        if k is not None:
                            if (str(k) == "block_index"):
                                #print("LastBlockCheck: " + str(v))
                                strReturn = v
                                return strReturn
        return strReturn
    except MaxRetryError:
        return None
# checks for msg from addy at block toBlockNumber
async def checkAssetsFromBlock(toBlockNumber):
    tempAssets = []
    for a in ASSETLIST:
        tempAssets.append(a.name)
    print("Checking Block: " + str(toBlockNumber) + " for assets...")
    parms = {"block_index":toBlockNumber}
    payload = {"method": "get_messages","params": parms,"jsonrpc": "2.0","id": 0}
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    jsonData = json.loads(response.text)
    #print("get_messages Check: " + str(jsonData))
    r=jsonData["result"]
    #print("get_messages Check: " + str(r))
    strReturn = "";
    for l in r:
        for k, v in l.items():
            aData = ''
            dData = ''
            mData = ''
            qData = ''
            if (str(k) == "bindings"):
                for k2, v2 in json.loads(str(v)).items():
                    if (str(k2) == 'asset'):
                        aData = str(v2)
                        #print("aData: " + aData)
                    if (str(k2) == 'destination'):
                        dData = str(v2)
                        #print("dData: " + dData)
                    if (str(k2) == 'memo'):
                        mData = str(v2)
                        #print("mData: " + mData)
                    if (str(k2) == 'quantity'):
                        qData = str(v2)
                        tknCount = v2
                        #print("qData: " + qData)
            if aData == regToken and dData == tokenWallet:
                my_string = mData
                my_string_bytes = bytes(my_string, encoding='utf-8')

                binary_string = codecs.decode(my_string_bytes, "hex")
                tknToAdd = str(binary_string, 'utf-8')
                print(regToken + ": #" + qData + " Token to Add: " + tknToAdd)
                if tknToAdd not in tempAssets:
                    tempAsset = asset(tknToAdd)
                    tempAsset.setBlock(toBlockNumber + (4032 * tknCount))
                    ASSETLIST.append(tempAsset)
                    print(tknToAdd + " Token added to block number: " + str(tempAsset.block))
                else:
                    tempAsset = await getAssetByName(tknToAdd)
                    tempAsset.setBlock(tempAsset.block + (4032 * tknCount))
                    print(tknToAdd + " Token updated to block number: " + str(tempAsset.block))

                    #ASSETLIST.append(tempAsset)

    return None

# checks for msg from addy at block toBlockNumber
async def checkMessageFromBlock(msg, toBlockNumber):
    #print("Checking Block: " + str(toBlockNumber))
    parms = {"block_index":toBlockNumber}
    payload = {"method": "get_messages","params": parms,"jsonrpc": "2.0","id": 0}
    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
    jsonData = json.loads(response.text)
    #print("get_messages Check: " + str(jsonData))
    r=jsonData["result"]
    #print("get_messages Check: " + str(r))
    strReturn = "";
    for l in r:
        for k, v in l.items():
            sData = ''
            tData = ''
            if (str(k) == "bindings"):
                for k2, v2 in json.loads(str(v)).items():
                    if (str(k2) == 'source'):
                        sData = str(v2)
                    if (str(k2) == 'text'):
                        tData = str(v2)
            if search(msg, tData):
                #print("Address Found: " + sData + " Message: " + tData)
                #print("success!!!")
                return sData
    return None


async def verifyUser(v, message):
    x = 1
    lastBlock = await getLastBlock()
    while lastBlock is None:
        lastBlock = await getLastBlock()
        await asyncio.sleep(sleepTime)
    tempBlock = lastBlock
    tempUser = user(message.author.name, message.author.id, False)
    while (not tempUser.isVerified and str(lastBlock) <= str(v.blockStart+6)):
        if lastBlock is not None:
            if (lastBlock > tempBlock):
                if (lastBlock >= tempBlock+2):
                    lastBlock = tempBlock+1
                tempBlock = lastBlock
                print("("+str(x)+")attempting to verify: " + message.author.name)
                address = await checkMessageFromBlock(v.alpha, lastBlock)
                if address is not None:
                    for member in USERLIST:
                        if str(member.id) == str(message.author.id):
                            member.setAddress(address)
                            #print("updated member "+member.name+" status!!!!")
                            await message.author.send("You have been verifyed to own the address: ||" + address +"||\n\n")
                            member.verify(True)
                            c = 0
                            for vs in verificationList:
                                if vs.name == member.name:
                                    verificationList.pop(c)
                                c = c + 1
                            tempUser = member
                            break

                x=x+1
        await asyncio.sleep(sleepTime)
        if not tempUser.isVerified:
            lastBlock = await getLastBlock()
            while lastBlock is None:
                lastBlock = await getLastBlock()
                await asyncio.sleep(sleepTime)
        if str(lastBlock) == str(v.blockStart+5):
            await message.author.send("We have not found you message broadcast yet!\n If you have not sent yet, your code expires in 1 more block.\n we recommend waiting and trying verify again after expiration! \n\n")


    if not tempUser.isVerified:
        c = 0
        for vs in verificationList:
            if vs.name == tempUser.name:
                verificationList.pop(c)
                break
            c = c + 1
        await message.author.send("Sorry we did not find your address in the last 6 block, please try again! \n\n")

    return



async def keyGen():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return x

async def createJsonFile():
    f = open("guilds.json", "x")
    information = {"Guilds":[],"Members":[],"Assets":[]}
    with open('guilds.json', 'w') as fp:
        json.dump(information, fp, indent=2)
    print("Created Guilds.Json")

@bot.event
async def on_member_join(member):
    for mem in USERLIST:
        if str(mem.id) == str(member.id):
            if not member.bot:
                USERLIST.append(user(member.name, str(member.id), str(False)))
    gName = member.guild.name
    for gs in GUILDLIST:
        if str(gs.name) == str(gName):
            inG = await userInGuildList(gs, member.id)
            if inG is False:
                gs.appendMember(str(member.id))


@bot.event
async def on_guild_join(guild):
    await appendGuild(guild)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            if discord.utils.get(guild.roles,name="BTC-Verified"):
                permText = "```We have proper permission to create roles! :D```"
            else:
                permText = "```We have DO NOT proper permission to create roles! \n Please put CounterCord role high enough to create roles!```"
            await channel.send('Hi! \n Welcome to CounterCord! \n\n CounterCord is a BTC/XCP asset verification tool! \n\n Users may verify their discord account by broadcasting a custom message \n Discord admins may add asset verification as a premium service! \n  check out the github:' + ccGithubURL + " \n or For all CounterCord info check out the site: "+ ccSiteURL + " \n\n" + permText)
            break

async def appendGuild(guild):
    tempGuildMemberIDs = []
    for m in USERLIST:
        tempGuildMemberIDs.append(str(m.id))
    for member in guild.members:
        if not member.bot:
            if str(member.id) not in tempGuildMemberIDs:
                tempGuildMemberIDs.append(str(member.id))
                tempMember = user(member.name, str(member.id), str(False))
                unverified.append(str(member.id))
                USERLIST.append(tempMember)
    tempGuild = guildsList(guild.name, guild.id)
    tempGuild.setMembers(unverified)
    GUILDLIST.append(tempGuild)

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@bot.event
async def on_message(message):
    if message.content == "cc help":
        response = "**All info on site:** " + ccSiteURL + "\n"
        response = response + '```\n ' + "cc verify \n - Used to verify your bitcoin address with CounterCord \n"
        response = response + '\n ' + "cc reverify \n - Used to reverify/change your bitcoin address with CounterCord \n"
        response = response + '\n ' + "cc address \n - Will return your verified Bitcoin address that CounterCord currently has \n"
        response = response + '\n ' + "cc assets \n - Will return Assets for given Arguments \n* can have arguments of (all, here, (me or None)) \n"
        response = response + '\n ' + "cc help \n - Will return this list \n"

        if message.author.guild_permissions.administrator:
            response = response + " \n ADMIN COMMANDS:"
            response = response + '\n ' + "cc rolelist \n - Will return a list of all members with role argument\n * reqires argument of (role)-Verified To kick anyone not on this list of members use optional args below\n * Optional end argument: purge true \n"
            response = response + '\n ' + "cc addresslist \n - Will DM a address list of all members with role argument\n * reqires argument of (role)-Verified \n"
            response = response + '\n ' + "cc purge \n - Will kick any member that does not have a BTC-Verified role \n"
            response = response + '\n ' + "cc add asset \n -  Will add a verified asset to your roles\n * reqires argument of ASSETNAME \n"
            response = response + '\n ' + "cc del asset \n -  Will remove a verified asset from your roles\n * reqires argument of ASSETNAME \n"
            await message.channel.send(response+'```')
        else:
            await message.channel.send(response+'```')

    if message.content == "cc verify":
        vCheck = False
        for mem in USERLIST:
            if str(mem.id) == str(message.author.id):
                for vs in verificationList:
                    if vs.name == mem.name:
                        vCheck = True
                if (str(mem.isVerified) == 'False') and vCheck is False:
                    response = message.author.mention + " Check DM to Verify"
                    await message.channel.send(response)
                    randomKey = await keyGen()
                    try:
                        await message.author.send("Hello, Lets get you verified! \n please broadcast a message on BTC/XCP blockchain\n within the next 6 blocks with the following code: " + str(randomKey) +" \n\n"
                        + "This process could take up to an hour... once you're verified, you will get a BTC-Verified role!")
                        ver = verification(str(message.author.name), randomKey, await getLastBlock())
                        verificationList.append(ver)
                        asyncio.create_task(verifyUser(ver, message))
                    except discord.Forbidden:
                        response = message.author.mention + "DM could not be sent. possibly DM's are OFF"
                        await message.channel.send(response)
                elif vCheck:
                    response = message.author.mention + " You are already attempting to verify, please check DM."
                    await message.channel.send(response)
                else:
                    response = message.author.mention + " You are verified with Address: ||" + mem.address + "||"
                    await message.channel.send(response)

    if message.content == "cc reverify":
        vCheck = False
        for mem in USERLIST:
            if str(mem.id) == str(message.author.id):
                for vs in verificationList:
                    if vs.name == mem.name:
                        vCheck = True
                if (str(mem.isVerified) == 'True') and vCheck is False:
                    mem.setAddress("")
                    mem.verify(False)
                    response = "Check DM to Verify"
                    await message.channel.send(response)
                    randomKey = await keyGen()
                    await message.author.send("Hello, Lets get you reverified! \n please broadcast a message on BTC/XCP blockchain with the following code: " + str(randomKey) +"\n\n"
                    + "This process could take up to an hour... once you're verified, you will still have a BTC-Verified role!")
                    ver = verification(str(message.author.name), randomKey, await getLastBlock())
                    verificationList.append(ver)
                    asyncio.create_task(verifyUser(ver, message))
                elif vCheck:
                    response = "You are already attempting to reverify, please check DM."
                    await message.channel.send(response)
                elif len(str(mem.address)) > 1:
                    response = "You are verified with Address: ||" + mem.address + "||"
                    await message.channel.send(response)
                else:
                    response = "The Address can't be found, or your last try expired, please try: \n cc verify"
                    await message.channel.send(response)

    if message.content == "cc address":
        for mem in USERLIST:
            if str(mem.id) == str(message.author.id):
                if (str(mem.isVerified) == 'True'):
                    response = "You are verified with Address: ||" + mem.address + "||"
                    await message.channel.send(response)
                else:
                    response = "It appears you arent verified yet! \n you can start verification with: \n  cc verify"
                    await message.channel.send(response)

    if message.content.startswith('cc asset'):
        if message.content == "cc assets all":
            tempAssetsList = []
            response = ""
            for a in ASSETLIST:
                tempAssetsList.append(a.name)
                response = response + '\n - ' + a.name + " Expiration Block: " + str(a.block)
            if len(tempAssetsList) > 0:
                response = "All Supported Assets List:" + '\n' + response
                await message.channel.send(response)
        if message.content == "cc assets here" or message.content == "cc assets this" or message.content == "cc assets discord" or message.content == "cc assets server":
            gID = message.guild.id
            tempAssetsList = []
            response = ""
            for gs in GUILDLIST:
                if str(gs.id) == str(gID):
                    for a in gs.assets:
                        tempAssetsList.append(a.name)
                        response = response + '\n - ' + a.name + " Expiration Block: " + str(a.block)
            if len(tempAssetsList) == 0:
                await message.channel.send('Sorry No Assets Found.')
            else:
                response = gs.name + " Assets List:" + '\n' + response
                await message.channel.send(response)

        if message.content == "cc assets" or message.content == "cc assets me" or message.content == "cc assets "+str(message.author.mention):
            tempAssetsList = []
            response = ""
            for mem in USERLIST:
                if str(mem.id) == str(message.author.id):
                    for a in mem.verifiedAssets:
                        tempAssetsList.append(a.name)
                        response = response + '\n - ' + a.name
            if len(tempAssetsList) == 0:
                await message.channel.send('Sorry No Assets Found.')
            else:
                response = message.author.name + " Assets List:" + '\n' + response
                await message.channel.send(response)

    if message.content.startswith('cc rolelist'):
        if message.author.guild_permissions.administrator:
            split = str(message.content).split(" ")
            if len(split) == 3:
                tempRoleName = split[2]
                count = 0
                response = ""
                if tempRoleName.endswith('-Verified'):
                    ar = discord.utils.get(message.guild.roles,name=str(tempRoleName))
                else:
                    ar = discord.utils.get(message.guild.roles,name=str(tempRoleName)+"-Verified")
                for mem in message.guild.members:
                    if ar in mem.roles:
                        response = response + '\n - ' + mem.name
                        count = count + 1
                if count == 0:
                    await message.channel.send('Sorry No Members Found.')
                else:
                    response = str(ar.name) + " List:" + '\n' + response
                    await message.channel.send(response)
            elif len(split) == 4:
                tempRoleName = split[2]
                count = 0
                response = ""
                if (split[3] == "purge"):
                    if tempRoleName.endswith('-Verified'):
                        ar = discord.utils.get(message.guild.roles,name=str(tempRoleName))
                    else:
                        ar = discord.utils.get(message.guild.roles,name=str(tempRoleName)+"-Verified")
                    for mem in message.guild.members:
                        if not mem.bot:
                            if ar not in mem.roles:
                                #await mem.kick(reason="unverified")
                                response = response + '\n - ' + mem.name
                                count = count + 1
                    if count == 0:
                        await message.channel.send('No Members Found.')
                    else:
                        response = str(ar.name) + " Kick List:" + '\n' + response  +"\n\n To kick all run command: \n cc rolelist <ROLENAME> purge true"
                        await message.channel.send(response)
            elif len(split) == 5:
                tempRoleName = split[2]
                count = 0
                response = ""
                if (split[3] == "purge") and ((split[4] == "true") or (split[4] == "True") or (split[4] == "True") or (split[4] == "t") or (split[4] == "T") or (split[4] == "Y") or (split[4] == "y") or (split[4] == "yes") or (split[4] == "YES") or (split[4] == "Yes")):
                    if tempRoleName.endswith('-Verified'):
                        ar = discord.utils.get(message.guild.roles,name=str(tempRoleName))
                    else:
                        ar = discord.utils.get(message.guild.roles,name=str(tempRoleName)+"-Verified")
                    for mem in message.guild.members:
                        if not mem.bot:
                            if ar not in mem.roles:
                                await mem.kick(reason="unverified")
                                response = response + '\n - ' + mem.name
                                count = count + 1
                    if count == 0:
                        await message.channel.send('No Members Found.')
                    else:
                        response = str(ar.name) + " Kick List:" + '\n' + response
                        await message.channel.send(response)
        else:
            await message.channel.send("Sorry this is a Admin command!")

    if message.content.startswith('cc addresslist'):
        if message.author.guild_permissions.administrator:
            split = str(message.content).split(" ")
            tempRoleName = split[2]
            count = 0
            response = ""
            if tempRoleName.endswith('-Verified'):
                ar = discord.utils.get(message.guild.roles,name=str(tempRoleName))
            else:
                ar = discord.utils.get(message.guild.roles,name=str(tempRoleName)+"-Verified")
            for mem in message.guild.members:
                if ar in mem.roles:
                    for u in USERLIST:
                        if str(u.id) == str(mem.id):
                            response = response + '\n - ' + u.address
                            count = count + 1
            if count == 0:
                await message.channel.send('Sorry No Assets Found.')
            else:
                response = str(ar.name) + " List:" + '\n' + response
                await message.author.send(response)
                await message.channel.send("Address List DM'd")
        else:
            await message.channel.send("Sorry this is a Admin command!")

    if message.content.startswith('cc purge'):
        split = str(message.content).split(" ")
        count = 0
        response = ""
        if message.author.guild_permissions.administrator:
            if len(split) == 2:
                    ar = discord.utils.get(message.guild.roles,name="BTC-Verified")
                    for mem in message.guild.members:
                        if not mem.bot:
                            if ar not in mem.roles:
                                #await mem.kick(reason="unverified")
                                response = response + '\n - ' + mem.name
                                count = count + 1
                    if count == 0:
                        await message.channel.send('No Members Found.')
                    else:
                        response = str(ar.name) + " Kick List:" + '\n' + response +"\n\n To kick all run command: \n cc purge true"
                        await message.channel.send(response)
            if len(split) == 3 and ((split[2] == "true") or (split[2] == "True") or (split[2] == "True") or (split[2] == "t") or (split[2] == "T") or (split[2] == "Y") or (split[2] == "y") or (split[2] == "yes") or (split[2] == "YES") or (split[2] == "Yes")):
                if message.author.guild_permissions.administrator:
                    ar = discord.utils.get(message.guild.roles,name="BTC-Verified")
                    for mem in message.guild.members:
                        if not mem.bot:
                            if ar not in mem.roles:
                                await mem.kick(reason="unverified")
                                response = response + '\n - ' + mem.name
                                count = count + 1
                    if count == 0:
                        await message.channel.send('No Members Found.')
                    else:
                        response = str(ar.name) + " Kick List:" + '\n' + response
                        await message.channel.send(response)
        else:
            await message.channel.send("Sorry this is a Admin command!")

    if message.content.startswith('cc add asset'):
        tAssetList = []
        for tas in ASSETLIST:
            tAssetList.append(tas.name)
        if message.author.guild_permissions.administrator:
            if message.content == "cc add asset default":
                aList = []
                for gs in GUILDLIST:
                    if str(gs.id) == str(message.guild.id):
                        for a in gs.assets:
                            aList.append(a.name)
                        if not defaultToken in aList:
                            gs.addAsset(asset(defaultToken))
                            msg = "Added " + defaultToken + " to this servers asset list!"
                            await message.channel.send(msg)
                            ar = discord.utils.get(message.guild.roles,name=str(defaultToken)+"-Verified")
                            if ar is None:
                                await message.guild.create_role(name=str(defaultToken)+"-Verified")
                            ar = discord.utils.get(message.guild.roles,name=str(defaultToken)+"-Verified")
                            msg = "Added Role: " + str(ar)
                            await message.channel.send(msg)
                        else:
                            msg = "Token " + defaultToken + " has already been added to this servers asset list!"
                            await message.channel.send(msg)
            else:
                split = str(message.content).split(" ")
                tempTokenName = split[3]
                if tempTokenName in tAssetList:
                    aList = []
                    for gs in GUILDLIST:
                        if str(gs.id) == str(message.guild.id):
                            for a in gs.assets:
                                aList.append(a.name)
                            if not tempTokenName in aList:
                                gs.addAsset(asset(tempTokenName))
                                msg = "Added " + tempTokenName + " to this servers asset list!"
                                await message.channel.send(msg)
                                ar = discord.utils.get(message.guild.roles,name=str(tempTokenName)+"-Verified")
                                if ar is None:
                                    await message.guild.create_role(name=str(tempTokenName)+"-Verified")
                                ar = discord.utils.get(message.guild.roles,name=str(tempTokenName)+"-Verified")
                                msg = "Added Role: " + str(ar)
                                await message.channel.send(msg)
                            else:
                                msg = "Token " + tempTokenName + " has already been added to this servers asset list!"
                                await message.channel.send(msg)
                else:
                    msg = "Token " + tempTokenName + " is not in the CounterCord asset list!"
                    await message.channel.send(msg)
        else:
            await message.channel.send("You arent an admin and can not use this command. sorry.")

    if message.content.startswith('cc remove asset') or message.content.startswith('cc rem asset') or message.content.startswith('cc del asset') or message.content.startswith('cc delete asset'):
        tAssetList = []
        split = str(message.content).split(" ")
        if message.author.guild_permissions.administrator:
            for tas in ASSETLIST:
                tAssetList.append(tas.name)
            if split[3] == "default":
                aList = []
                for gs in GUILDLIST:
                    if str(gs.id) == str(message.guild.id):
                        for a in gs.assets:
                            aList.append(a.name)
                        if defaultToken in aList:
                            gs.delAsset(defaultToken)
                            msg = "removed " + defaultToken + " from this servers asset list!"
                            await message.channel.send(msg)
                            ar = discord.utils.get(message.guild.roles,name=str(defaultToken)+"-Verified")
                            if ar is not None:
                                await ar.delete()
                            msg = "Removed Role: " + str(defaultToken)+"-Verified"
                            await message.channel.send(msg)
                        else:
                            msg = "Token " + defaultToken + " has already been removed from this servers asset list!"
                            await message.channel.send(msg)
            else:
                tempTokenName = split[3]
                if tempTokenName in tAssetList:
                    aList = []
                    for gs in GUILDLIST:
                        if str(gs.id) == str(message.guild.id):
                            for a in gs.assets:
                                aList.append(a.name)
                            if tempTokenName in aList:
                                gs.delAsset(tempTokenName)
                                msg = "removed " + tempTokenName + " from this servers asset list!"
                                await message.channel.send(msg)
                                ar = discord.utils.get(message.guild.roles,name=str(tempTokenName)+"-Verified")
                                if ar is not None:
                                    await ar.delete()
                                #ar = discord.utils.get(message.guild.roles,name=str(tempTokenName)+"-Verified")
                                msg = "Removed Role: " + str(tempTokenName)+"-Verified"
                                await message.channel.send(msg)
                            else:
                                msg = "Token " + tempTokenName + " has already been removed from this servers asset list!"
                                await message.channel.send(msg)
                else:
                    msg = "Token " + tempTokenName + " is not in the CounterCord asset list!"
                    await message.channel.send(msg)
        else:
            await message.channel.send("You arent an admin and can not use this command. sorry.")

bot.run(tok)
