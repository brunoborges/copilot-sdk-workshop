using System.Diagnostics;

namespace hello_copilot_sdk.Helpers;

public record CopilotStatus(
    bool IsInstalled,
    bool IsTokenSet,
    bool IsAuthenticated,
    string? ErrorMessage);

public static class CliChecker
{
    public static bool IsReady(CopilotStatus status)
        => status.IsInstalled && (status.IsTokenSet || status.IsAuthenticated);

    public static async Task<CopilotStatus> CheckCopilotStatusAsync()
    {
        var isTokenSet = !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("GH_TOKEN"));

        try
        {
            var version = await RunCommandAsync("copilot", "--version");
            if (string.IsNullOrWhiteSpace(version))
            {
                return new CopilotStatus(false, isTokenSet, false, "Copilot CLI is installed but returned no version.");
            }
        }
        catch (Exception ex)
        {
            return new CopilotStatus(false, isTokenSet, false, $"Copilot CLI not found: {ex.Message}");
        }

        try
        {
            var authOutput = await RunCommandAsync("copilot", "auth status");
            var isAuthenticated = authOutput.Contains("Logged in", StringComparison.OrdinalIgnoreCase)
                               || authOutput.Contains("Authenticated", StringComparison.OrdinalIgnoreCase);

            if (!isAuthenticated && !isTokenSet)
            {
                return new CopilotStatus(true, false, false, "Not authenticated. Run 'copilot auth login' or set GH_TOKEN.");
            }

            return new CopilotStatus(true, isTokenSet, isAuthenticated, null);
        }
        catch (Exception ex)
        {
            return new CopilotStatus(true, isTokenSet, false, $"Could not verify auth status: {ex.Message}");
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

        if (process.ExitCode != 0 && string.IsNullOrWhiteSpace(output))
        {
            throw new InvalidOperationException(error);
        }

        return output + error;
    }
}
