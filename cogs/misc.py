import collections
import datetime
import re
import traceback

import discord
from discord.ext import commands

import ao3

import html2text


class Misc(commands.Cog):

    def format_ao3(self, work):
        def make_link(elm):
            return "[{}]({})".format(elm,
                                     elm.url.replace("(", "%28").replace(")", "%29"))

        def make_str(lst):
            return [str(elm) for elm in lst]

        def make_links(lst):
            return [make_link(elm) for elm in lst]

        disp = discord.Embed()
        disp.title = work.title
        disp.url = work.url
        disp.colour = 9437184
        disp.timestamp = datetime.datetime.combine(work.published, datetime.time())
        infodict = collections.OrderedDict()
        infodict["Rating"] = ", ".join(make_str(work.rating))
        infodict["Archive Warnings"] = "No Archive Warnings Apply" if not work.warnings else ", ".join(
            make_str(work.warnings))
        infodict["Category"] = ", ".join(make_str(work.category))
        if work.fandoms:
            infodict['Fandom'] = ", ".join(make_links(work.fandoms))
        infodict['Language'] = work.language
        if work.series:
            infodict['Series'] = "Part {} of {}".format(work.series_idx, make_link(work.series))
        infodict['Stats'] = "Words: {} Hits: {} Kudos: {} Chapters: {}/{}".format(work.words,
                                                                                  work.hits,
                                                                                  work.kudos,
                                                                                  work.published_chapters,
                                                                                  "?"
                                                                                  if work.total_chapters is None else
                                                                                  work.total_chapters)
        info = "\n".join(["**{}**: {}".format(k, v)
                          for k, v
                          in infodict.items()])
        disp.description = """by {}\n\n{}""".format(", ".join(make_links(work.authors)),
                                                    info)
        total_len = len(disp.description)
        if work.relationship:
            val = ", ".join(make_links(work.relationship))
            if len(val) > 1024:
                val = ", ".join(make_str(work.relationship))
            if len(val) > 1024:
                val = val[:1021] + "..."
            total_len += len(val)
            disp.add_field(name="Relationships",
                           value=val,
                           inline=False)
        if work.characters:
            val = ", ".join(make_links(work.characters))
            if len(val) > 1024:
                val = ", ".join(make_str(work.characters))
            if len(val) > 1024:
                val = val[:1021] + "..."
            total_len += len(val)
            disp.add_field(name="Characters",
                           value=val,
                           inline=False)
        if work.additional_tags:
            val = ", ".join(make_links(work.additional_tags))
            if len(val) > 1024:
                val = ", ".join(make_str(work.additional_tags))
            if len(val) > 1024:
                val = val[:1021] + "..."
            total_len += len(val)
            disp.add_field(name="Additional Tags",
                           value=val,
                           inline=False)
        val = html2text.html2text(work.summary)
        if len(val) > 1024:
            val = val[:1021] + "..."
        if total_len + len(val) > 6000:
            if total_len < 5997:
                val = val[:5997 - total_len] + "..."
            else:
                return discord.Embed(description=":( I tried but that fic has too much info.")
        disp.add_field(name="Description",
                       value=val,
                       inline=False)
        return disp

    @commands.command()
    async def ao3(self, ctx: commands.Context, msg: str):
        """
        Attach a preview of an Ao3 Work
        """

        try:
            wid = int(msg)
        except ValueError:
            mtch = re.match("^https?://(?:www.)?archiveofourown.org/works/(\d*).*$", msg)
            if mtch is None:
                await ctx.send("Error: Please provide either a workID or a URL")
                return
            wid = int(mtch.group(1))
        async with ctx.typing():
            api = ao3.AO3()
            api.session.headers.update({'User-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"})
            try:
                work = api.work(id=wid)
            except Exception as ex:
                await ctx.send("Error: Can't find a work with that ID/URL")
                print("".join(traceback.format_exception(None, ex, None)))
                return
            try:
                disp = self.format_ao3(work)
            except Exception as ex:
                await ctx.send("Sorry, something went wrong parsing that fic.")
                print("".join(traceback.format_exception(None, ex, None)))
                print(work._html)
                return
            await ctx.send(embed=disp)
