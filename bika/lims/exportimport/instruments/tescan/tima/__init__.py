from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser

class TimaCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self._columns = []

    def _parseline(self, line):
        line = line.replace('"', '').strip()
        return self._parse_data_row(line)

    def _splitline(self, line):
        return [token.strip() for token in line.split(',')]

    # "AA00228","12/11/2003","20:49:24", ,0,"Cromo (Cr)","Cr",205.56,1.298161935e-003, ,"mg/muestra",
    # The above line shows the data row from the file however this method
    # is called it will not have any double quotes as they were removed in the _parseline step.
    def _parse_data_row(self, line):
        if not self._columns:
            self._columns = self._splitline(line)
            return 0
        else:
            if not line.strip():
                return 0

            rawdict = {}
            cell_values = [token.strip() for token in line.split(',')]
            for idx, result in enumerate(cell_values):
                if len(self._columns) <= idx:
                    self.err("Orphan value in column ${index}",
                             mapping={"index": str(idx + 1)},
                             numline=self._numline)
                    break
                rawdict[self._columns[idx]] = result

            acode = rawdict.get('Elem', '')
            if not acode:
                self.err("No Analysis Code defined",
                         numline=self._numline)
                return 0

            rid = rawdict.get('Sample ID')
            if not rid:
                self.err("No Sample ID defined",
                         numline=self._numline)
                return 0

            #errors = rawdict.get('Errors', '')
            #errors = "Errors: %s" % errors if errors else ''
            #notes = rawdict.get('Notes', '')
            #notes = "Notes: %s" % notes if notes else ''

            outdict={}
            outdict[acode]={'DefaultResult': 'Conc (Samp)',
                            'Conc (Samp)': rawdict['Conc (Samp)'],}


            #rawdict[acode] = rawdict['Conc (Samp)']
            #rawdict['DefaultResult'] = 'Conc (Samp)'
            #rawdict['Remarks'] = ' '.join([errors, notes])
            #rawres = self.getRawResults().get(rid, [])
            #raw = rawres[0] if len(rawres) > 0 else {}
            #raw[acode] = rawdict

            # The false argument means that when the result is added it will be associated with
            # a matching Sample Id if one already exists.
            self._addRawResult(rid, outdict, False)

            return 0