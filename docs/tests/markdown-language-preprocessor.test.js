'use strict';

const assert = require('node:assert/strict');
const { getLanguage } = require('../language-registry.js');
const { preprocessLanguageDirectives } = require('../markdown-language-preprocessor.js');

const preprocess = (markdown, languageId) =>
    preprocessLanguageDirectives(markdown, languageId, getLanguage);

assert.equal(
    preprocess('Shared\n:::language dotnet\n.NET only\n:::\n:::language python\nPython only\n:::\nEnd', 'dotnet'),
    'Shared\n.NET only\nEnd'
);
assert.equal(
    preprocess('Shared\n:::language dotnet\n.NET only\n:::\n:::language python\nPython only\n:::\nEnd', 'python'),
    'Shared\nPython only\nEnd'
);
assert.throws(
    () => preprocess(':::language dotnet\n:::language python\n:::\n:::', 'dotnet'),
    /cannot be nested/
);
assert.throws(() => preprocess(':::language unknown\n:::', 'dotnet'), /unknown language/);
assert.throws(() => preprocess(':::language dotnet\nUnclosed', 'dotnet'), /not closed/);
assert.throws(() => preprocess(':::', 'dotnet'), /closing directive has no open/);
assert.throws(() => preprocess(':::unexpected', 'dotnet'), /expected :::language/);

console.log('Markdown language preprocessor tests passed.');
