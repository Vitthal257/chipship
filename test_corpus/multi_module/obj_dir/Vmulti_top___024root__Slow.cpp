// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vmulti_top.h for the primary calling header

#include "Vmulti_top__pch.h"

void Vmulti_top___024root___ctor_var_reset(Vmulti_top___024root* vlSelf);

Vmulti_top___024root::Vmulti_top___024root(Vmulti_top__Syms* symsp, const char* namep)
 {
    vlSymsp = symsp;
    vlNamep = strdup(namep);
    // Reset structure values
    Vmulti_top___024root___ctor_var_reset(this);
}

void Vmulti_top___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vmulti_top___024root::~Vmulti_top___024root() {
    VL_DO_DANGLING(std::free(const_cast<char*>(vlNamep)), vlNamep);
}
