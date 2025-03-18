const { ActivityHandler, TurnContext } = require('botbuilder');
const { AzureKeyCredential, TextAnalysisClient } = require('@azure/ai-language-text');

// CLU API key and endpoint from Azure portal
const key = process.env.CLUK_API_KEY;  // Use environment variables for security
const endpoint = process.env.CLUK_ENDPOINT;

const client = new TextAnalysisClient(endpoint, new AzureKeyCredential(key));

module.exports = async function (context, req) {
    const userMessage = req.body.text;  // Get text from incoming request

    // Call CLU to analyze the user's message
    const response = await client.analyze({
        text: userMessage,
        language: 'en'
    });

    const intent = response.result.intents[0]?.category;  // Get the intent
    const entities = response.result.entities;  // Get the entities

    context.res = {
        status: 200,
        body: {
            intent,
            entities
        }
    };
};
