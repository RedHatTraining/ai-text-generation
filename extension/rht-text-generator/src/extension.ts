// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import Axios from "axios";
import { exec } from "child_process";
import { COMPLETION_TRIGGERS } from "./triggers";



// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const provider: vscode.CompletionItemProvider = { provideCompletionItems };

	context.subscriptions.push(
		vscode.languages.registerCompletionItemProvider(
			{ pattern: "**"},
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
	const MAX_LINES: number = config.get("lines") || 3;
	const lines = [];

	for (let lineOffset = 0; lineOffset < MAX_LINES; lineOffset++ ) {
		const lineNumber = Math.max(0, position.line - lineOffset);
		const line = document.lineAt(lineNumber).text.trimEnd();
		lines.unshift(line);
	}
	const text = lines.join("\n");

	const predictionLength: number = config.get("length") || 3;

	const server: string = config.get("server") || "";
	let suggestions: string[] = await generateSuggestions(text, predictionLength, server);

	return suggestions.map(suggestion => {
		const tail = suggestion.replace(text, "").trim();
		return new vscode.CompletionItem(tail);
	});
}

async function generateSuggestions(line: string, predictionLength: number, server: string) {
	let suggestions: string[] = [];
	try {
		const response = await Axios.get<[string]>(
			`http://${server}/?text=${line}&length=${predictionLength}`
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
