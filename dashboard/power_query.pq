// Power Query M templates. Not executed in Power BI in this environment.
// Paste each named expression into a separate Blank Query's Advanced Editor.
// First create DataFolder (Text), then fxPermitOpsCsv, then the three tables.

// Query: DataFolder — change this path on the machine running Power BI.
"C:\PermitOps\outputs\reporting"

// Query: fxPermitOpsCsv — generic UTF-8 CSV loader; preserves header names.
(FileName as text, ColumnTypes as list) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "\" & FileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, ColumnTypes, "en-CA")
in
    Typed

// Query: fact_reporting
fxPermitOpsCsv("fact_reporting.csv", {
    {"permit_key", type text}, {"permit_type", type text}, {"revision_num", type text},
    {"application_date", type date}, {"issued_date", type date}, {"completed_date", type date},
    {"source_dataset", type text}, {"status", type text}, {"as_of_date", type date},
    {"application_eligible", type logical}, {"review_eligible", type logical},
    {"active_eligible", type logical}, {"active_unissued_eligible", type logical},
    {"review_days", Int64.Type}, {"active_age_days", Int64.Type}, {"completion_days", Int64.Type}
})

// Query: dim_date
fxPermitOpsCsv("dim_date.csv", {
    {"calendar_date", type date}, {"year", Int64.Type}, {"month", Int64.Type}, {"month_start", type date}
})

// Query: dim_permit_type
fxPermitOpsCsv("dim_permit_type.csv", {{"permit_type", type text}})
