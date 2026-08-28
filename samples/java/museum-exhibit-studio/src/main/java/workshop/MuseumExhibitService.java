package workshop;

import com.github.copilot.SystemMessageMode;
import com.github.copilot.rpc.SessionConfig;
import com.github.copilot.rpc.SystemMessageConfig;

import java.time.Duration;
import java.util.List;

public final class MuseumExhibitService {
    public static final Duration GENERATION_TIMEOUT = Duration.ofSeconds(120);

    private final CuratorClient client;

    public MuseumExhibitService(CuratorClient client) {
        this.client = client;
    }

    public GeneratedExhibit generate(Iterable<String> approvedFacts, String model) throws Exception {
        String prompt = CuratorPrompts.buildExhibitPrompt(approvedFacts);
        CuratorSession session = null;
        try {
            client.start();
            session = client.createSession(createSessionConfiguration(model));
            String content = session.sendAndWait(prompt, GENERATION_TIMEOUT.toMillis());
            if (content == null || content.isBlank()) {
                throw new IllegalStateException("The curator returned no exhibit content.");
            }
            return new GeneratedExhibit(content, ExhibitValidator.validate(content));
        } finally {
            try {
                if (session != null) {
                    session.disconnect();
                }
            } finally {
                client.stop();
            }
        }
    }

    public static SessionConfig createSessionConfiguration(String model) {
        SessionConfig configuration = new SessionConfig()
                .setClientName("museum-exhibit-studio")
                .setAvailableTools(List.of())
                .setStreaming(false)
                .setSystemMessage(new SystemMessageConfig()
                        .setMode(SystemMessageMode.REPLACE)
                        .setContent(CuratorPrompts.SYSTEM_MESSAGE));
        if (model != null && !model.isBlank()) {
            configuration.setModel(model);
        }
        return configuration;
    }

    public record GeneratedExhibit(String content, ExhibitValidation validation) {
    }
}
