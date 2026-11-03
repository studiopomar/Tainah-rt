/*
 * Copyright (c) 2022. YuzukiTsuru <GloomyGhost@GloomyGhost.com>.
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License v3.0 as published by
 *  the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * You should have received a copy of the GNU Lesser General Public License v3.0
 * along with this software. If not, see <http://www.gnu.org/licenses/>.
 */

#include "WorldModule.h"

#include "Utils/LOG.h"
#include "Utils/Timer.h"

#include <world/dio.h>
#include <world/stonemask.h>
#include <world/cheaptrick.h>
#include <world/harvest.h>
#include <world/d4c.h>

#include <utility>

WorldModule::WorldModule(double *x, int x_length, int fs, lessConfigure config) : x(x), x_length(x_length), configure(std::move(config)) {
    this->worldPara.fs = fs;
    this->worldPara.frame_period = configure.audio_model_frame_period;

    YALL_DEBUG_ << "Generate F0 from PCM file.";

    Timer timer;

    if (configure.f0_mode == lessConfigure::F0_MODE::F0_MODE_DIO) {
        timer.SetTimer();
        F0EstimationDio();
        YALL_EVAL_ << timer.GetTimer("DIO F0 Estimation: ");
    } else if (configure.f0_mode == lessConfigure::F0_MODE::F0_MODE_HARVEST) {
        timer.SetTimer();
        F0EstimationHarvest();
        YALL_EVAL_ << timer.GetTimer("HARVEST F0 Estimation: ");
    } else {
        throw std::runtime_error("F0 Estimation Mode Error.");
    }

    YALL_DEBUG_ << "Generate Envelope from PCM file and F0.";
    timer.SetTimer();
    SpectralEnvelopeEstimation();
    YALL_EVAL_ << timer.GetTimer("Spectral Envelope Estimation: ");

    YALL_DEBUG_ << "Generate Aperiodicity.";
    timer.SetTimer();
    AperiodicityEstimation();
    YALL_EVAL_ << timer.GetTimer("Aperiodicity Estimation: ");
}

WorldModule::~WorldModule() {
    delete[] this->worldPara.time_axis;
    delete[] this->worldPara.f0;
    for (int i = 0; i < this->worldPara.f0_length; ++i) {
        delete[] this->worldPara.spectrogram[i];
        delete[] this->worldPara.aperiodicity[i];
    }
    delete[] this->worldPara.spectrogram;
    delete[] this->worldPara.aperiodicity;
}

WorldPara WorldModule::GetModule() {
    return this->worldPara;
}

void WorldModule::F0EstimationDio() {
    DioOption option = {0};
    InitializeDioOption(&option);

    option.frame_period = this->worldPara.frame_period;
    option.speed = configure.f0_speed;

    option.f0_floor = configure.f0_dio_floor;
    if (configure.f0_ceiling > option.f0_floor) option.f0_ceil = configure.f0_ceiling;
    option.allowed_range = configure.f0_allow_range;

    this->worldPara.f0_length = GetSamplesForDIO(this->worldPara.fs, x_length, this->worldPara.frame_period);
    this->worldPara.f0 = new double[this->worldPara.f0_length];
    this->worldPara.time_axis = new double[this->worldPara.f0_length];
    auto *refined_f0 = new double[this->worldPara.f0_length];

    Dio(x, x_length, this->worldPara.fs, &option, this->worldPara.time_axis, this->worldPara.f0);

    StoneMask(x, x_length, this->worldPara.fs, this->worldPara.time_axis, this->worldPara.f0, this->worldPara.f0_length, refined_f0);

    for (int i = 0; i < this->worldPara.f0_length; ++i) {
        this->worldPara.f0[i] = refined_f0[i];
    }

    delete[] refined_f0;
}

void WorldModule::F0EstimationHarvest() {
    HarvestOption option = {0};
    InitializeHarvestOption(&option);

    option.frame_period = this->worldPara.frame_period;
    option.f0_floor = configure.f0_harvest_floor;
    if (configure.f0_ceiling > option.f0_floor) option.f0_ceil = configure.f0_ceiling;

    this->worldPara.f0_length = GetSamplesForHarvest(this->worldPara.fs, x_length, this->worldPara.frame_period);
    this->worldPara.f0 = new double[this->worldPara.f0_length];
    this->worldPara.time_axis = new double[this->worldPara.f0_length];

    Harvest(x, x_length, this->worldPara.fs, &option, this->worldPara.time_axis, this->worldPara.f0);
}

void WorldModule::SpectralEnvelopeEstimation() {
    CheapTrickOption option = {0};
    InitializeCheapTrickOption(this->worldPara.fs, &option);

    option.f0_floor = configure.f0_cheap_trick_floor;
    option.fft_size = [&]() {
        if (configure.custom_fft_size) {
            return configure.fft_size;
        } else {
            return GetFFTSizeForCheapTrick(this->worldPara.fs, &option);
        }
    }();

    this->worldPara.fft_size = option.fft_size;
    this->worldPara.spectrogram = new double *[this->worldPara.f0_length];
    for (int i = 0; i < this->worldPara.f0_length; ++i) {
        this->worldPara.spectrogram[i] = new double[this->worldPara.fft_size / 2 + 1];
    }

    CheapTrick(x, x_length, this->worldPara.fs, this->worldPara.time_axis, this->worldPara.f0, this->worldPara.f0_length, &option,
               this->worldPara.spectrogram);
}

void WorldModule::AperiodicityEstimation() {
    D4COption option = {0};
    InitializeD4COption(&option);

    option.threshold = configure.ap_threshold;

    this->worldPara.aperiodicity = new double *[this->worldPara.f0_length];
    for (int i = 0; i < this->worldPara.f0_length; ++i) {
        this->worldPara.aperiodicity[i] = new double[this->worldPara.fft_size / 2 + 1];
    }

    D4C(x, x_length, this->worldPara.fs, this->worldPara.time_axis, this->worldPara.f0, this->worldPara.f0_length, this->worldPara.fft_size, &option,
        this->worldPara.aperiodicity);
}
