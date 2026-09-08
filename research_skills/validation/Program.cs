using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;
using System.Text.Json;

if (args.Length != 1) return 2;
using OpenXmlPackage document = Path.GetExtension(args[0]).ToLowerInvariant() switch
{
    ".xlsx" => SpreadsheetDocument.Open(args[0], false),
    ".pptx" => PresentationDocument.Open(args[0], false),
    ".docx" => WordprocessingDocument.Open(args[0], false),
    _ => throw new ArgumentException("Unsupported Office artifact")
};
var errors = new OpenXmlValidator().Validate(document).ToList();
Console.WriteLine(JsonSerializer.Serialize(new { errors = errors.Count,
    issues = errors.Take(10).Select(e => new { type = e.Id,
        part = e.Part?.Uri.ToString(), path = e.Path?.XPath }) }));
return errors.Count == 0 ? 0 : 1;
