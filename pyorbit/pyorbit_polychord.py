from classes.common import *
from classes.model_container_polychord import ModelContainerPolyChord
from classes.input_parser import yaml_parser, pars_input
from classes.io_subroutines import nested_sampling_save_to_cpickle, nested_sampling_load_from_cpickle, nested_sampling_create_dummy_file
import os
import sys
import argparse

__all__ = ["pyorbit_polychord", "yaml_parser"]

""" 
def show(filepath):
    # open the output (pdf) file for the user
    if os.name == 'mac': subprocess.call(('open', filepath))
    elif os.name == 'nt': os.startfile(filepath)
"""


def pyorbit_polychord(config_in, input_datasets=None, return_output=None):


    output_directory = './' + config_in['output'] + '/polychord/'

    reloaded_mc = False


    try:
        mc = nested_sampling_load_from_cpickle(output_directory, prefix='')
    #    reloaded_mc = True
    except:
        pass

    if reloaded_mc:
        mc.model_setup()
        mc.initialize_logchi2()
        #mc.results_resumen(flatchain)
    else:
        mc = ModelContainerPolyChord()
        pars_input(config_in, mc, input_datasets)

        if mc.nested_sampling_parameters['shutdown_jitter']:
            for dataset in mc.dataset_dict.itervalues():
                dataset.shutdown_jitter()

        mc.model_setup()
        mc.create_variables_bounds()
        mc.initialize_logchi2()

        mc.create_starting_point()

        mc.results_resumen(None, skip_theta=True)

        mc.output_directory = output_directory



    #os.system("mkdir -p " + output_directory + "/clusters")
    #os.system("mkdir -p " +output_directory + "chains/clusters")

    print
    print 'Reference Time Tref: ', mc.Tref
    print
    print '*************************************************************'
    print


    settings = PolyChordSettings(nDims=mc.ndim, nDerived=0)

    settings.file_root = 'pyorbit'
    settings.base_dir = output_directory

    for key_name, key_value in mc.nested_sampling_parameters.items():

        if hasattr(settings, key_name):
            setattr(settings, key_name, key_value)

        print key_name, key_value

    if 'nlive_mult' in mc.nested_sampling_parameters:
        setattr(settings, 'nlive', mc.ndim * mc.nested_sampling_parameters['nlive_mult'])

    if 'num_repeats_mult' in mc.nested_sampling_parameters:
        setattr(settings, 'num_repeats', mc.ndim * mc.nested_sampling_parameters['num_repeats_mult'])

    if 'include_priors' in mc.nested_sampling_parameters:
        mc.include_priors = mc.nested_sampling_parameters['include_priors']

    output = PyPolyChord.run_polychord(mc.polychord_call, nDims=mc.ndim, nDerived=0, settings=settings,
                                       prior=mc.polychord_priors)

    paramnames = [('p%i' % i, r'\theta_%i' % i) for i in range(mc.ndim)]
    paramnames += [('r*', 'r')]
    output.make_paramnames_files(paramnames)

    nested_sampling_save_to_cpickle(mc)

    print
    print 'PolyChord COMPLETED'
    print

    """ A dummy file is created to let the cpulimit script to proceed with the next step"""
    nested_sampling_create_dummy_file(mc)

    if return_output:
        return mc
    else:
        return
