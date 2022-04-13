from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from betterShinden import *


class ShindenCMD:
    def __init__(self):
        self.shinden = Shinden()
        self.session = PromptSession()

        self.currentlyWatching = None
        self.currentEpisode = None

        self.username = None
        self.password = None

    async def chooseEpisodePlayer(self, episode):
        playersInfo = await self.shinden.getEpisodePlayers(episode)

        if len(playersInfo) == 0:
            print("No players found")
            return

        print("{0:<6}{1:<12}{2:>8}{3:>8}{4:>12}".format("ID", "Player", "Audio", "Subs", "Resolution"))
        for playerInfo in playersInfo:
            print("{0:<6}{1:<12}{2:>8}{3:>8}{4:>12}".format(
                playersInfo.index(playerInfo),
                playerInfo['player'],
                playerInfo['lang_audio'],
                playerInfo['lang_subs'],
                playerInfo['max_res'],
            ))

        playerInfo = playersInfo[int(input("player id: "))]

        player = await self.shinden.getPlayer(playerInfo['online_id'])

        print(player)

    async def start(self):
        while True:
            with patch_stdout():
                command = await self.session.prompt_async(">>> ", is_password=False)

            match command.split(' '):
                case ["help"]:
                    print("login <username> <password>")
                    print("search <anime name>")
                    print("getAnimeEpisodes <animeUrl>")
                    print("getEpisodePlayers <episodeUrl>")
                    print("getPlayer <onlineId>")
                    print("watch <animeUrl>")
                    print("next")
                    print("skip <NumberOfEpsToSkip>")
                    print("goto <NumberOfEp>")
                    print("get")
                    print("exit")
                case ["login"]:
                    with patch_stdout(): self.username = await PromptSession().prompt_async("Username: ", is_password=False)
                    with patch_stdout(): self.password = await PromptSession().prompt_async("Password: ", is_password=True)

                    await self.shinden.login(self.username, self.password)

                case ["watch", url]:
                    await self.shinden.login(self.username, self.password)

                    self.currentlyWatching = await self.shinden.getAnimeEpisodes(url)
                    self.currentEpisode = 1

                    await self.chooseEpisodePlayer(self.currentlyWatching[-self.currentEpisode]['url'])

                    self.currentEpisode += 1

                case ["skip", n]:
                    self.currentEpisode += int(n)

                case ["next"]:
                    await self.shinden.login(self.username, self.password)
                    await self.chooseEpisodePlayer(self.currentlyWatching[-self.currentEpisode]['url'])

                    self.currentEpisode += 1
                case ["search", *name]:
                    pa(await self.shinden.searchAnime(' '.join(name)))
                case ["getAnimeEpisodes", url]:
                    pa(await self.shinden.getAnimeEpisodes(url))
                case ["getEpisodePlayers", url]:
                    pa(await self.shinden.getEpisodePlayers(url))
                case ["getPlayer", id]:
                    print(await self.shinden.getPlayer(id))
                case ["exit" | "quit" | "close"]:
                    break
                case ["aa"]:
                    print(dumps(await self.shinden.getAnimeListAll()))
                case ["episodes", *name]:
                    url = (await self.shinden.searchAnime(' '.join(name)))[0]['url']
                    eps = await self.shinden.getAnimeEpisodes(url)
                    players = []
                    for ep in eps:
                        pls = await self.shinden.getEpisodePlayers(ep['url'])
                        for pl in pls:
                            players.append(self.shinden.getPlayer(pl['online_id']))
                    pa(await gather(*players))
                case ['']:
                    pass
                case _:
                    print("unknown command or command usage. Check 'help'.")

    async def close(self):
        await self.shinden.close()


async def main():
    shindenCMD = ShindenCMD()
    await shindenCMD.start()
    await shindenCMD.close()

if __name__ == "__main__":
    run(main())
