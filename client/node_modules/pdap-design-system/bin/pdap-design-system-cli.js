#!/usr/bin/env node
import minimist from 'minimist';
import cli from '../cli';
import process from 'process';

// Convert argv to object keyed by argName where --argName is what is passed to CLI
const args = minimist(process.argv);

switch (true) {
	case args['copy-assets']:
		cli.copyAllAssets(args);
		break;
	case args['copy-images']:
		cli.copyImageAssets(args);
		break;
	case args['copy-styles']:
		cli.copyStyleAssets(args);
		break;
	default:
		console.log(
			'No option argument was passed to pdap-design-system CLI.',
			'\n Current options are:',
			'\n --copy-assets: Copy all assets to assets/ (default) or custom path passed to optional --to argument.',
			'\n --copy-images: Copy only image assets to assets/ (default) or custom path passed to optional --to argument.',
			'\n --copy-styles: Copy only CSS assets to assets/ (default) or custom path passed to optional --to argument.'
		);
		break;
}
