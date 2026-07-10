using System.Diagnostics;

namespace hello_copilot_sdk.Helpers;

public record CopilotCliStatus(
    bool IsInstalled,
    string? ErrorMessage);

public static class CliChecker
{
    public static async Task<CopilotCliStatus> CheckCopilotCliAsync()
    {
        try
        {
            var version = await RunCommandAsync("copilot", "--version");
            if (string.IsNullOrWhiteSpace(version))
            {
                return new CopilotCliStatus(false, "Copilot CLI is installed but returned no version.");
            }

            return new CopilotCliStatus(true, null);
        }
        catch (System.ComponentModel.Win32Exception ex)
        {
            return new CopilotCliStatus(false, $"Copilot CLI not found: {ex.Message}");
        }
        catch (InvalidOperationException ex)
        {
            return new CopilotCliStatus(false, $"Copilot CLI could not run: {ex.Message}");
        }
    }

    private static async Task<string> RunCommandAsync(string command, string arguments)
    {
        var psi = new ProcessStartInfo
        {
            FileName = command,
            Arguments = arguments,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = Process.Start(psi)
            ?? throw new InvalidOperationException($"Could not start process: {command}");

        await process.WaitForExitAsync();
        var output = await process.StandardOutput.ReadToEndAsync();
        var error = await process.StandardError.ReadToEndAsync();

        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException(
                string.IsNullOrWhiteSpace(error) ? output : error);
        }

        return output;
    }
}
