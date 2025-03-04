// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import Axios from "axios";
import { exec } from "child_process";
import { COMPLETION_TRIGGERS } from "./triggers";


const leadingSpacesRegex = /^[^\S\r\n]+/;
let outputTab: vscode.OutputChannel;


// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const provider: vscode.CompletionItemProvider = { provideCompletionItems };
	outputTab = vscode.window.createOutputChannel('rht-text-generator');

	context.subscriptions.push(
		vscode.languages.registerCompletionItemProvider(
			[{ language: "asciidoc" }, { language: "latex" }, { language: "markdown" }, { language: "plaintext" }],
			provider,
			...COMPLETION_TRIGGERS
		)
	);
}

// this method is called when your extension is deactivated
export function deactivate() { }


async function provideCompletionItems(
	document: vscode.TextDocument,
	position: vscode.Position
): Promise<vscode.CompletionList> {
	const items = await getCompletionsListItemsFor(document, position);
	return new vscode.CompletionList(items, true);
}


async function getCompletionsListItemsFor(
	document: vscode.TextDocument,
	position: vscode.Position
): Promise<vscode.CompletionItem[]> {
	const prompt = generatePrompt(document, position);
	outputTab.appendLine("%%%%%%%%%%%%%%%%%%%%%% PROMPT %%%%%%%%%%%%%%%%%%%%%%");
	outputTab.appendLine(prompt);
	outputTab.appendLine("%%%%%%%%%%%%%%%%%%%%%% /PROMPT %%%%%%%%%%%%%%%%%%%%%%");

	outputTab.appendLine("%%%%%%%%%%%%%%%%%%%%%% SUGGESTIONS %%%%%%%%%%%%%%%%%%%%%%");
	const suggestions = (await generateSuggestions(prompt))
		.map((suggestion, idx) => {
			const item = new vscode.CompletionItem(suggestion.replace(leadingSpacesRegex, ""));
			item.sortText = idx.toString();
			outputTab.appendLine(`* ${item.label}`);
			return item;
		}).filter(item => item.label.trim().length > 0);
	outputTab.appendLine("%%%%%%%%%%%%%%%%%%%%%% /SUGGESTIONS %%%%%%%%%%%%%%%%%%%%%%");

	return suggestions;
}

function generatePrompt(document: vscode.TextDocument, position: vscode.Position): string {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const promptTemplate: string = config.get("promptTemplate") || "{{{prefix}}}";
	const prefix = getTextPrefix(document, position);
	const suffix = getTextSuffix(document, position);

	return promptTemplate.replace("{{{prefix}}}", prefix).replace("{{{suffix}}}", suffix);
}


/**
 * Get the text from the current position back to a specific number of lines
 */
function getTextPrefix(document: vscode.TextDocument, position: vscode.Position): string {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const MAX_LINES: number = config.get("lines") || 3;
	const currentLineNumber = position.line;
	const rangeEnd = position;
	const rangeStartLine = Math.max(0, currentLineNumber - MAX_LINES);
	const rangeStart = new vscode.Position(rangeStartLine, 0);
	const text = document.getText(new vscode.Range(rangeStart, rangeEnd));
	return text;
}

function getTextSuffix(document: vscode.TextDocument, position: vscode.Position): string {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const MAX_LINES: number = config.get("lines") || 3;
	const numLines = Math.floor(MAX_LINES / 3);
	const rangeStart = position;
	const rangeEnd = new vscode.Position(position.line + numLines, 0);
	const text = document.getText(new vscode.Range(rangeStart, rangeEnd));
	return text.trim();
}

async function generateSuggestions(text: string) {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const api: string = config.get("api") || "";

	if (api === "openai") {
		return await makeRequestToOpenAIAPI(text);
	}

	return await makeRequestToCustomAPI(text);
}

async function makeRequestToOpenAIAPI(text: string) {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const server: string = config.get("server") || "";
	const maxTokens: number = config.get("maxTokens") || 3;
	const model: string = config.get("model") || "";
	const apiKey: string = config.get("apiKey") || "";

	const requestBody = {
		model,
		prompt: text,
		n: 5, // Generate multiple completions
		max_tokens: maxTokens,
		temperature: 0.5
	};

	const headers = {
		"Content-Type": "application/json",
		"Authorization": `Bearer ${apiKey}`
	};
	const apiURL = `${server}/completions`.replace("//completions", "/completions");

	let suggestions: string[] = [];

	try {
		const response = await Axios.post(apiURL, requestBody, { headers });
		suggestions = response.data.choices.map((choice: any) => choice.text);
	} catch (error) {
		if (error.response) {
			// The request was made and the server responded with a status code
			// that falls out of the range of 2xx
			console.log(error.response.data);
			console.log(error.response.status);
			console.log(error.response.headers);
		} else if (error.request) {
			// The request was made but no response was received
			// `error.request` is an instance of XMLHttpRequest in the browser and an instance of
			// http.ClientRequest in node.js
			console.log(error.request);
		} else {
			// Something happened in setting up the request that triggered an Error
			console.log('Error', error.message);
		}
	}
	return suggestions;
}

async function makeRequestToCustomAPI(text: string) {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const server: string = config.get("server") || "";
	const maxTokens: number = config.get("maxTokens") || 3;

	let suggestions: string[] = [];
	try {
		const response = await Axios.get<[string]>(
			`http://${server}/?text=${text}&length=${maxTokens}`
		);
		suggestions = response.data;
	} catch (error) {
		if (error.response) {
			// The request was made and the server responded with a status code
			// that falls out of the range of 2xx
			console.log(error.response.data);
			console.log(error.response.status);
			console.log(error.response.headers);
		} else if (error.request) {
			// The request was made but no response was received
			// `error.request` is an instance of XMLHttpRequest in the browser and an instance of
			// http.ClientRequest in node.js
			console.log(error.request);
		} else {
			// Something happened in setting up the request that triggered an Error
			console.log('Error', error.message);
		}
	}
	return suggestions;
}

