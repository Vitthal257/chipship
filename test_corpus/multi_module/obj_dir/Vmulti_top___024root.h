// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vmulti_top.h for the primary calling header

#ifndef VERILATED_VMULTI_TOP___024ROOT_H_
#define VERILATED_VMULTI_TOP___024ROOT_H_  // guard

#include "verilated.h"


class Vmulti_top__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vmulti_top___024root final {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(clk,0,0);
    VL_IN8(addr,3,0);
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VstlPhaseResult;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*3:0*/ __Vtrigprevexpr___TOP__addr__0;
    CData/*0:0*/ __VicoDidInit;
    CData/*0:0*/ __VicoPhaseResult;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__1;
    CData/*0:0*/ __VactPhaseResult;
    CData/*0:0*/ __VnbaPhaseResult;
    VL_IN16(in_b,15,0);
    SData/*15:0*/ __Vtrigprevexpr___TOP__in_b__0;
    VL_IN(in_a,31,0);
    VL_OUT(alu_out,31,0);
    VL_OUT(reg_out,31,0);
    IData/*31:0*/ __Vtrigprevexpr___TOP__in_a__0;
    IData/*31:0*/ __VactIterCount;
    VlUnpacked<IData/*31:0*/, 8> multi_top__DOT__u_regfile__DOT__mem;
    VlUnpacked<QData/*63:0*/, 1> __VstlTriggered;
    VlUnpacked<QData/*63:0*/, 2> __VicoTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VactTriggered;
    VlUnpacked<QData/*63:0*/, 1> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vmulti_top__Syms* vlSymsp;
    const char* vlNamep;

    // CONSTRUCTORS
    Vmulti_top___024root(Vmulti_top__Syms* symsp, const char* namep);
    ~Vmulti_top___024root();
    VL_UNCOPYABLE(Vmulti_top___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
