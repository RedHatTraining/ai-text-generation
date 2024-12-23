// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import Axios from "axios";
import { exec } from "child_process";
import { COMPLETION_TRIGGERS } from "./triggers";


const leadingSpacesRegex = /^[^\S\r\n]+/;


// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const provider: vscode.CompletionItemProvider = { provideCompletionItems };

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

	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const text = getText(document, position);

	const predictionLength: number = config.get("length") || 3;

	const server: string = config.get("server") || "";
	let suggestions: string[] = await generateSuggestions(text, predictionLength, server);

	return suggestions.map((suggestion, idx) => {
		const item = new vscode.CompletionItem(suggestion.replace(leadingSpacesRegex, ""));
		item.sortText = idx.toString();
		return item;
	}).filter(item => item.label.trim().length > 0);
}

/**
 * Get the text from the current position back to a specific number of lines
 */
function getText(document: vscode.TextDocument, position: vscode.Position): string {
	const config = vscode.workspace.getConfiguration("rht-text-generator");
	const MAX_LINES: number = config.get("lines") || 3;
	const currentLineNumber = position.line;
	const rangeEnd = position;
	const rangeStartLine = Math.max(0, currentLineNumber - MAX_LINES);
	const rangeStart = new vscode.Position(rangeStartLine, 0);
	const text = document.getText(new vscode.Range(rangeStart, rangeEnd));
	return text;
}

async function generateSuggestions(line: string, predictionLength: number, server: string) {
	let suggestions: string[] = [];
	const body = { text: line, length: predictionLength };

	try {
		console.log(line);
		console.log(predictionLength);
		const response = await Axios.post<[string]>(`http://${server}/`, body);
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
