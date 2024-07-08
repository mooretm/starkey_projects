""" Class that does all the G23-specific juggling of 
    verifit and estat data files

    Written by: Travis M. Moore
    Created: Dec 07, 2022
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd


class G23Model():
    """ Class that does all the G23-specific juggling of 
        verifit and estat data files.

        Returns:
            final_data: a dataframe of verifit and estat
                data, including measured minus target
                differences
    """
    def __init__(self, verifit, estat, form_key, session):
        self.verifit = verifit.copy()
        self.estat = estat.copy()
        self.form_key = form_key
        self.session = session


    def get_data(self):
        """ Main function 
        """
        print('\n'+'-'*60)
        print(f'g23model: Preparing {self.session} data...')
        self._add_sub_and_form_cols()
        self._filter_by_session()
        self._match_subs()
        self._get_diffs()
        print('Done!')



    ##################################
    # Dataframe Reorganization Funcs #
    ##################################
    def _add_sub_and_form_cols(self):
        """ Create subject column from file name
        """
        # Verifit
        self.verifit.insert(loc=0, column='sub', value= '')
        self.verifit.insert(loc=1, column='form_factor', value='')
        self.verifit.reset_index(inplace=True, drop=True)
        for ii in range(0,len(self.verifit)):
            # Add subject ID
            sub = self.verifit.iloc[ii, 2].split('_')[0]
            self.verifit.iloc[ii, 0] = sub
            self.verifit.iloc[ii, 1] = self.form_key[sub]['Form_Factor']
        self.verifit.sort_values(by='sub')

        # Estat
        self.estat.insert(loc=0, column='sub', value= '')
        self.estat.reset_index(inplace=True, drop=True)
        for ii in range(0,len(self.estat)):
            self.estat.loc[ii, 'sub'] = self.estat.loc[ii, 'filename'].split('_')[0]
        self.estat.sort_values(by='sub')
    

    def _filter_by_session(self):
        # Only verifit files contain the session (BestFit/EndStudy)
        self.verifit = self.verifit[
            self.verifit['filename'].str.contains(self.session)]


    def _match_subs(self):
        """ Identify common subjects across verifit and 
            estat dfs after filtering
        """
        vsubs = self.verifit['sub'].unique()
        esubs = self.estat['sub'].unique()
        common_subs = list(set(vsubs) & set(esubs))

        # Create new dataframe of common subjects with all data
        self.verifit = self.verifit[self.verifit['sub'].isin(common_subs)].copy()
        self.estat = self.estat[self.estat['sub'].isin(common_subs)].copy()
        self.verifit.sort_values(by=['sub', 'level', 'form_factor'], inplace=True)
        self.estat.sort_values(by=['sub', 'level', 'form_factor'], inplace=True)


    def _get_diffs(self):
        """ Find measured SPL - e-STAT target and add a difference column
        """
        # Add estat values to verifit dataframe
        self.verifit['estat_target'] = list(self.estat['estat_target'])

        self.final_data = self.verifit.copy()
        # Subtract
        self.final_data['measured-estat'] = self.final_data['measured'] - self.final_data['estat_target']
        
        # Assign column names to use with verifitmodel plotting function
        self.final_data.rename(columns={
            'filename': 'file',
            'sub': 'filename',
            'measured-target': 'measured-NAL',
            'measured-estat': 'measured-target'
            }, inplace=True
        )


    def compare_estat(self, bestfit, endstudy):
        common_subs = list(set(bestfit['filename'].unique()) & set(endstudy['filename'].unique()))
        best = bestfit[bestfit['filename'].isin(common_subs)].copy()
        end = endstudy[endstudy['filename'].isin(common_subs)].copy()
        best.sort_values(by=['filename', 'form_factor'], inplace=True)
        end.sort_values(by=['filename', 'form_factor'], inplace=True)

        best.drop(['targets', 'measured-NAL', 'measured-target'], axis=1, inplace=True)
        best.rename(columns={'measured': 'bestfit_spl'}, inplace=True)
        best['endstudy_spl'] = list(end['measured'])
        self.combo = best.copy()
        self.combo['best-end'] = self.combo['bestfit_spl'] - self.combo['endstudy_spl']
        self.combo['best-target'] = self.combo['bestfit_spl'] - self.combo['estat_target']
        self.combo['end-target'] = self.combo['endstudy_spl'] - self.combo['estat_target']
        return self.combo


    def gather_freqs(self): 
        for ii in range(0, len(self.R['freq'])):
            if (int(self.R.iloc[ii, 3]) < 1000):
                self.R.iloc[ii, 3] = 'low'
            elif (int(self.R.iloc[ii, 3]) >= 1000) and (int(self.R.iloc[ii, 3]) < 4500):
                self.R.iloc[ii, 3] = 'mid'
            elif (int(self.R.iloc[ii, 3]) >= 4500):
                self.R.iloc[ii, 3] = 'high'


    def gather_levels(self):
        for ii in range(0, len(self.R['level'])):
            val = self.R.iloc[ii, 5]
            if (val == 'L1') or (val == 'R1'):
                self.R.iloc[ii, 5] = 'soft'
            elif (val == 'L2') or (val == 'R2'):
                self.R.iloc[ii, 5] = 'avg'
            elif (val == 'L3') or (val == 'R3'):
                self.R.iloc[ii, 5] = 'loud'


    def collapse_forms(self, data):
        # Make copy of provided dataframe
        self.collapsed = data.copy()

        # Get current form factor index values
        forms_list = list(self.collapsed['form_factor'])
        
        # Create list of new index vals
        new_form_vals = []
        for val in forms_list:
            if val == 'RIC':
                new_form_vals.append('RIC')
            elif val == 'MRIC':
                new_form_vals.append('RIC')
            elif val == 'ITC':
                new_form_vals.append('Wireless Custom')
            elif val == 'ITE':
                new_form_vals.append('Wireless Custom')
            elif val == 'CIC':
                new_form_vals.append('Wired Custom')
            elif val == 'IIC':
                new_form_vals.append('Wired Custom')
            else: 
                print('Invalid form factor!!')
                return

        # Replace old index vals with new index vals
        # Drop original form factor index column
        self.collapsed['form_factor'] = new_form_vals
        self.collapsed.to_csv('./G23 REM Data/collapsed_REM_data.csv')
        return self.collapsed


    def export_to_R(self):
        # Copy the combo df
        self.R = self.combo.copy()

        # Convert freqs to high/mid/low
        self.gather_freqs()

        # Collapse across left and right ears by level
        self.gather_levels()

        # Drop and/or rename columns
        self.R.drop(['file', 'unit'], axis=1, inplace=True)
        self.R.rename(columns={
            'filename': 'sub',
            'best-end': 'best_minus_end',
            'best-target': 'best_minus_target',
            'end-target': 'end_minus_target'
            }, inplace=True)

        # Write wide format to csv
        self.R.to_csv('BestEndWide.csv', index=False)

        # Copy the copy df
        self.BestEndLong = self.R.copy()

        # Rename columns
        self.BestEndLong.rename(columns={
            'bestfit_spl': 'bestfit', 
            'endstudy_spl': 'endstudy'
            }, inplace=True
        )

        # Melt to long format
        self.BestEndLong = pd.melt(self.BestEndLong, 
            id_vars=['sub', 'form_factor', 'freq', 'level'],
            value_vars=['bestfit', 'endstudy', 'estat_target']
        )
        self.BestEndLong.rename(columns={'variable': 'session'}, inplace=True)
        self.BestEndLong.to_csv('BestEndLong.csv', index=False)


    ######################################
    # Plot eSTAT BestFit - EndStudy Data #
    ######################################
    def plot_best_minus_end(self, data, verifit_model, calc, show=None, save=None):
        combo = data.copy()
        combo.rename(columns={'best-end': 'measured-target'}, inplace=True)
        plot_labels = {'ylabs': np.repeat('BestFit - Final', 3)}
        #forms = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
        forms = list(data['form_factor'].unique())
        for form in forms:
            temp = combo[combo['form_factor']==form]
            plot_labels['save_title'] = f"./G23 REM Data/eSTAT_best-end_{form}.png"
            verifit_model.plot_diffs(
                data=temp, 
                title=f"eSTAT BestFit minus Final ({form})",
                calc=calc,
                show=show,
                save=save,
                **plot_labels
                )


    ####################################
    # Plot eSTAT Target Deviation Data #
    ####################################
    def plot_estat_target_deviation(self, data, session_label, verifit_model, calc, show=None, save=None):
        print('\n'+'-'*60)
        print("g23model: Creating eSTAT Target Deviation plots...")
        plot_labels = {}
        forms = list(data['form_factor'].unique())
        for form in forms:
            temp = data[data['form_factor']==form]
            plot_labels['save_title'] = f"./G23 REM Data/eSTAT_{session_label}_{form}.png"
            verifit_model.plot_diffs(
                data=temp, 
                title=f"Measured SPL minus e-STAT Target ({form}: {session_label})",
                calc=calc,
                show=show,
                save=save,
                **plot_labels
                )
        print("Done!")
    # def plot_estat_target_deviation(self, bestfit, endstudy, verifit_model, calc, show=None, save=None):
    #     print('\n'+'-'*60)
    #     print("g23model: Creating eSTAT Target Deviation plots...")
    #     plot_labels = {}
    #     dfs = [bestfit, endstudy]
    #     labels = ['BestFit', 'EndStudy']
    #     forms = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
    #     for ii, df in enumerate(dfs):
    #         for form in forms:
    #             temp = df.final_data[df.final_data['form_factor']==form]
    #             plot_labels['save_title'] = f"./G23 REM Data/eSTAT_{labels[ii]}_{form}.png"
    #             verifit_model.plot_diffs(
    #                 data=temp, 
    #                 title=f"Measured SPL minus e-STAT Target ({form}: {labels[ii]})",
    #                 calc=calc,
    #                 show=show,
    #                 save=save,
    #                 **plot_labels
    #                 )
    #     print("Done!")


    ######################################
    # Plot Verifit Target Deviation Data #
    ######################################
    def plot_nal_target_deviation(self, bestfit, endstudy, verifit_model, calc, show=None, save=None):
        best = bestfit.final_data.copy()
        end = endstudy.final_data.copy()

        print('\n'+'-'*60)
        print("g23model: Creating NAL plots...")
        # New column names
        names = {
            'measured-target': 'measured-estat', 
            'measured-NAL': 'measured-target'
        }

        # Rename columns
        best.rename(columns=names, inplace=True)
        end.rename(columns=names, inplace=True)

        # Plot NAL-NL2 deviations from target
        plot_labels = {}
        dfs = [best, end]
        labels = ['BestFit', 'EndStudy']
        forms = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
        for ii, df in enumerate(dfs):
            for form in forms:
                temp = df[df['form_factor']==form]
                plot_labels['save_title'] = f"./G23 REM Data/NAL_{labels[ii]}_{form}.png"
                verifit_model.plot_diffs(
                    data=temp, 
                    title=f"Measured SPL minus NAL-NL2 Targets ({form}: {labels[ii]})",
                    calc=calc,
                    show=show,
                    save=save,
                    **plot_labels
                    )
        print("Done!\n")
