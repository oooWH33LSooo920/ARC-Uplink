import discord
from discord.ext import commands
from discord import app_commands
from channel_settings import load_channels, save_channels
from updater import WeeklyTrialsUpdater

class WeeklyTrialsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setweeklytrials", description="Set this channel for ARC Weekly Trials updates.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setweeklytrials(self, interaction: discord.Interaction):
        print("[WeeklyTrialsCog] Entered setweeklytrials command")
        import traceback
        from bot import weekly_trials_updaters
        channels = load_channels()
        guild_id = str(interaction.guild.id)
        if guild_id not in channels:
            channels[guild_id] = {}
        channels[guild_id]["weekly_trials"] = interaction.channel_id
        save_channels(channels)
        await interaction.response.send_message("This channel is now set for ARC Weekly Trials updates.")
        try:
            print("[WeeklyTrialsCog] Instantiating WeeklyTrialsUpdater...")
            updater = WeeklyTrialsUpdater(
                bot=self.bot,
                channel_id=interaction.channel_id
            )
            print("[WeeklyTrialsCog] WeeklyTrialsUpdater instantiated.")
            updater.start()
            weekly_trials_updaters[interaction.guild.id] = updater  # Keep strong reference
            print(f"[WeeklyTrialsCog] Started WeeklyTrialsUpdater for guild {interaction.guild.id} channel {interaction.channel_id}")
            try:
                await updater.update_message()
                print(f"[WeeklyTrialsCog] Called update_message for guild {interaction.guild.id} channel {interaction.channel_id}")
            except Exception as e:
                print(f"[WeeklyTrialsCog] Error posting initial weekly trials message: {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"[WeeklyTrialsCog] Error starting WeeklyTrialsUpdater: {e}")
            traceback.print_exc()

    @app_commands.command(name="weekly_trials", description="Show the current ARC Weekly Trials rotation.")
    async def weekly_trials(self, interaction: discord.Interaction):
        from weekly_trials import fetch_weekly_trials, build_weekly_trials_embed
        trials = fetch_weekly_trials()
        if not trials:
            await interaction.response.send_message("Could not fetch weekly trials at this time.")
            return
        embed = build_weekly_trials_embed(trials)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(WeeklyTrialsCog(bot))
