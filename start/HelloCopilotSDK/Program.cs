using GitHub.Copilot;

Console.WriteLine("Hello, GitHub Copilot SDK!");

await using var client = new CopilotClient();
await client.StartAsync();

var response = await client.PingAsync("hello");
Console.WriteLine(response.Message);