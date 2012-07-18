#!/usr/bin/env python
"""
Pique runtime.
"""
import pique
import sys
import pickle


def run( name, ipfile, bgfile, mapfile, alpha, l_thresh, pickle_file ) :
    
    # set logfile
    logfile = name + '.log'
    
    pique.msg( logfile, 'starting run for project : ' + name )
    
    # log inputs
    pique.msg( logfile, '  -> IP file  : ' + ipfile   )
    pique.msg( logfile, '  -> BG file  : ' + ipfile   )
    pique.msg( logfile, '  -> map file : ' + mapfile  )
    pique.msg( logfile, '  -> alpha    : ' + str(alpha)    )
    pique.msg( logfile, '  -> l_thresh : ' + str(l_thresh) )
    
    # load the data
    pique.msg( logfile, 'loading data...' )
    D = pique.data.PiqueData( ipfile, bgfile, mapfile, name=name )
    
    pique.msg( logfile, '  found contigs :' )
    for contig in D.data.keys() :
        pique.msg( logfile, '    ' + contig )
        pique.msg( logfile, '      length : ' + str(D.data[contig]['length']) )
        for r in D.data[contig]['regions'] :
            start = str( r['start'] )
            stop  = str( r['stop']  )
            pique.msg( logfile, '      analysis region : ' + start + ':' + stop )
        for m in D.data[contig]['masks'] :
            start = str( m['start'] )
            stop  = str( m['stop']  )
            pique.msg( logfile, '      masking region  : ' + start + ':' + stop )
    
    # start analysis workbench
    pique.msg( logfile, 'creating analysis workbench...' )
    PA = pique.analysis.PiqueAnalysis( D )
    
    # run filters
    pique.msg( logfile, 'running filters...' )
    
    for ar_name in PA.data.keys() :
        pique.msg( logfile, '  :: applying filters to analysis region ' + ar_name )
        PA.apply_filter( ar_name, alpha, l_thresh )
    
    # find peaks
    pique.msg( logfile, 'finding peaks...' )
    for ar_name in PA.data.keys() :
        PA.find_peaks(ar_name)
        pique.msg( logfile, '  peaks ' + ar_name + ' : ' + str(len(PA.data[ar_name]['peaks'])) )
        pique.msg( logfile, '     noise threshold  : ' + str(PA.data[ar_name]['N_thresh']) )
        pique.msg( logfile, '     filter threshold : ' + str(PA.data[ar_name]['n_thresh']) )
        pique.msg( logfile, '     normalizations   : ' + ', '.join( map(str, PA.data[ar_name]['norms']) ) )
    
    # if a pickle file was requested, write it
    pique.msg( logfile, 'pickling analysis workbench...' )
    if pickle_file :
        pickle.dump( PA, open( name + '.pickle', 'w' ) )
    
    # write output files
    pique.msg( logfile, 'writing output files...' )
    pique.fileIO.writepeaksGFF(  name + '.gff',      PA.data )
    pique.fileIO.writebookmarks( name + '.bookmark', PA.data, name=name )
    pique.fileIO.writeQP(        name + '.qp',       PA.data )
    pique.fileIO.writepeakTSV(   name + '.peak.tsv', PA.data )
    pique.fileIO.writetrack(     name + '.IP.track', D.data  )
    pique.fileIO.writetrack(     name + '.BG.track', D.data, track='BG' )

    # done!
    pique.msg( logfile, 'run completed.' )

