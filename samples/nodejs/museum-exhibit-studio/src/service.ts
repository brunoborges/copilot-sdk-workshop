import { CopilotClient, type SessionConfig } from "@github/copilot-sdk";
import { buildExhibitPrompt, systemMessage } from "./prompts.js";
import { validateExhibit, type ExhibitValidation } from "./validator.js";

export const generationTimeoutMs = 120_000;

export interface CuratorSession {
  sendAndWait(prompt: string, timeout?: number): Promise<
    { data: { content: string } } | undefined
  >;
  disconnect(): Promise<void>;
}

export interface CuratorClient {
  start(): Promise<void>;
  createSession(configuration: SessionConfig): Promise<CuratorSession>;
  stop(): Promise<unknown>;
}

export interface GeneratedExhibit {
  content: string;
  validation: ExhibitValidation;
}

export function createSessionConfiguration(model?: string): SessionConfig {
  return {
    clientName: "museum-exhibit-studio",
    model: model?.trim() || undefined,
    availableTools: [],
    streaming: false,
    systemMessage: {
      mode: "replace",
      content: systemMessage,
    },
  };
}

export class MuseumExhibitService {
  constructor(private readonly client: CuratorClient) {}

  async generate(approvedFacts: Iterable<string>, model?: string): Promise<GeneratedExhibit> {
    const prompt = buildExhibitPrompt(approvedFacts);
    let session: CuratorSession | undefined;

    try {
      await this.client.start();
      session = await this.client.createSession(createSessionConfiguration(model));
      const response = await session.sendAndWait(prompt, generationTimeoutMs);
      const content = response?.data.content;
      if (!content?.trim()) throw new Error("The curator returned no exhibit content.");
      return { content, validation: validateExhibit(content) };
    } finally {
      try {
        await session?.disconnect();
      } finally {
        await this.client.stop();
      }
    }
  }
}

export function createCopilotCuratorClient(): CuratorClient {
  return new CopilotClient();
}
