"""

"""
from . import TimaCSVParser
title = "TESCAN TIMA"
from bika.lims.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter
import json
import traceback

def Import(context, request):
    infile = request.form['upload_file']

    parser = TimaCSVParser(infile)

    if parser:
        importer = AnalysisResultsImporter(parser=parser,
                                           context=context)
        trace=''
        try:
            importer.process()
        except:
            trace = traceback.format_exc()

        errors = importer.errors
        logs = importer.logs
        warns = importer.warns

        if trace:
            errors.append(trace)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)
