let
    Source = Csv.Document(File.Contents(Parameter_FilePath),[Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers,{{"Activity ID", type text},{"Activity Name", type text},{"WBS Code", type text},{"Discipline", type text},{"Area", type text},{"BL Start", type date},{"BL Finish", type date},{"Start", type date},{"Finish", type date},{"Planned Duration", Int64.Type},{"Budgeted Labor Units", type number},{"Physical % Complete", type number},{"Activity Status", type text},{"Data Date", type date}}),
    DisciplineFilled = Table.ReplaceValue(Typed,null,"Unassigned",Replacer.ReplaceValue,{"Discipline"}),
    ProgressBounded = Table.TransformColumns(DisciplineFilled, {{"Physical % Complete", each Number.Min(1, Number.Max(0, _)), type number}}),
    UniqueActivities = Table.Distinct(ProgressBounded,{"Activity ID"})
in
    UniqueActivities
