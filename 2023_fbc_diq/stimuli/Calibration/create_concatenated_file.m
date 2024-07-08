%% script to generate concatenated file from all recorded files for calibration
% Author: Henning Schepker <henning_Schepker AT starkey.de>
% Date: 2023-12-06

clear
close all
clc


% szFilename = 'HS_impulses_concat.wav';
% szDatafolderMain = '\\starfile\Dept\Research and Development\FBC\DiQ\Round2_TRL6\Yes_No_Data\Headphone_study_final\HS_Impulses';

szFilename = 'speech_shortened_and_filtered_concat.wav';
szDatafolderMain = '\\starfile\Dept\Research and Development\FBC\DiQ\Round2_TRL6\Yes_No_Data\Headphone_study_final\Shortened_Filtered_Recordings_Static_fbp_case1';

cSubfolders = {'Fit1_SetA','Fit1_SetA_Vol8dB',...
                'Fit1_SetE','Fit1_SetE_Vol8dB',...
                'Fit2_SetA','Fit2_SetA_Vol8dB',...
                'Fit2_SetE','Fit2_SetE_Vol8dB',...
                'Fit3_SetA','Fit3_SetE'};


vConcatFile = [];

for iSubfolder = 1:length(cSubfolders)
    % read files
    stFiles = dir(fullfile(szDatafolderMain,cSubfolders{iSubfolder},'*.wav'));
    for iFile = 1:length(stFiles)
        [y,fs] = audioread(fullfile(stFiles(iFile).folder,stFiles(iFile).name));
        
        % identify signal as part that exceeds rms by more than 10dB
        idxStart = find(10.*log10(y(:,1).^2) > 20.*log10(rms(y(:,1)))+10,1,'first');
        idxEnd = find(10.*log10(y(:,1).^2) > 20.*log10(rms(y(:,1)))+10,1,'last');

        % add another 100ms to end
        idxEnd = min(length(y),idxEnd+fs*0.1);

        % sanity check for plotting
%         figure
%         plot(y(:,1))
%         hold all
%         plot(idxStart:idxEnd,y(idxStart:idxEnd,1))

        % concat
        vConcatFile = cat(1,vConcatFile,y(idxStart:idxEnd,:));

    end
end

audiowrite(szFilename,vConcatFile,fs);

