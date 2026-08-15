// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"

bool Vtop___024root___trigger_anySet__ico(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___trigger_anySet__ico\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtop___024root___eval_phase__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VicoExecute;
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__ico
        vlSelfRef.__VicoTriggered[0U] = ((0xfffffffffffffffeULL 
                                          & vlSelfRef.__VicoTriggered[0U]) 
                                         | (IData)((IData)(vlSelfRef.__VicoFirstIteration)));
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtop___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
    }
#endif
    __VicoExecute = Vtop___024root___trigger_anySet__ico(vlSelfRef.__VicoTriggered);
    if (__VicoExecute) {
        {
            // Inlined CFunc: _eval_ico
            if ((1ULL & vlSelfRef.__VicoTriggered[0U])) {
                {
                    // Inlined CFunc: _ico_sequent__TOP__0
                    vlSelfRef.alu__DOT__clk = vlSelfRef.clk;
                    vlSelfRef.alu__DOT__rst_n = vlSelfRef.rst_n;
                    vlSelfRef.alu__DOT__op = vlSelfRef.op;
                    vlSelfRef.alu__DOT__a = vlSelfRef.a;
                    vlSelfRef.alu__DOT__b = vlSelfRef.b;
                    vlSelfRef.result = vlSelfRef.alu__DOT__result;
                    vlSelfRef.zero = vlSelfRef.alu__DOT__zero;
                    vlSelfRef.overflow = vlSelfRef.alu__DOT__overflow;
                }
            }
        }
    }
    return (__VicoExecute);
}

bool Vtop___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___trigger_anySet__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

void Vtop___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Vtop___024root___eval_phase__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((((~ (IData)(vlSelfRef.alu__DOT__rst_n)) 
                                                           & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__alu__DOT__rst_n__0)) 
                                                          << 1U) 
                                                         | ((IData)(vlSelfRef.alu__DOT__clk) 
                                                            & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__alu__DOT__clk__0))))));
        vlSelfRef.__Vtrigprevexpr___TOP__alu__DOT__clk__0 
            = vlSelfRef.alu__DOT__clk;
        vlSelfRef.__Vtrigprevexpr___TOP__alu__DOT__rst_n__0 
            = vlSelfRef.alu__DOT__rst_n;
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtop___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Vtop___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    return (0U);
}

void Vtop___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Vtop___024root___eval_phase__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Vtop___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_sequent__TOP__0
                    if (vlSelfRef.alu__DOT__rst_n) {
                        vlSelfRef.alu__DOT__zero = 
                            (0U == vlSelfRef.alu__DOT__result);
                        if (VL_UNLIKELY(((8U & (IData)(vlSelfRef.alu__DOT__op))))) {
                            VL_WRITEF_NX("[%0t] %%Error: alu.sv:46: Assertion failed in %m: ALU: Illegal opcode 4'b%b executed at time %0t\n",5, 'M',vlSymsp->name(),"alu", 'T',-9
                                         , '#',64,VL_TIME_UNITED_Q(1000)
                                         , '#',4,(IData)(vlSelfRef.alu__DOT__op)
                                         , '#',64,VL_TIME_UNITED_Q(1000));
                            VL_STOP_MT("/home/virtual/chipship/test_corpus/cocotb_alu/../alu_module/alu.sv", 46, "");
                            vlSelfRef.alu__DOT__result = 0U;
                        } else if ((4U & (IData)(vlSelfRef.alu__DOT__op))) {
                            if ((2U & (IData)(vlSelfRef.alu__DOT__op))) {
                                if (VL_UNLIKELY(((1U 
                                                  & (IData)(vlSelfRef.alu__DOT__op))))) {
                                    VL_WRITEF_NX("[%0t] %%Error: alu.sv:46: Assertion failed in %m: ALU: Illegal opcode 4'b%b executed at time %0t\n",5, 'M',vlSymsp->name(),"alu", 'T',-9
                                                 , '#',64,VL_TIME_UNITED_Q(1000)
                                                 , '#',4,(IData)(vlSelfRef.alu__DOT__op)
                                                 , '#',64,VL_TIME_UNITED_Q(1000));
                                    VL_STOP_MT("/home/virtual/chipship/test_corpus/cocotb_alu/../alu_module/alu.sv", 46, "");
                                    vlSelfRef.alu__DOT__result = 0U;
                                } else {
                                    vlSelfRef.alu__DOT__result 
                                        = (vlSelfRef.alu__DOT__a 
                                           >> (0x0000001fU 
                                               & vlSelfRef.alu__DOT__b));
                                }
                            } else {
                                vlSelfRef.alu__DOT__result 
                                    = ((1U & (IData)(vlSelfRef.alu__DOT__op))
                                        ? (vlSelfRef.alu__DOT__a 
                                           << (0x0000001fU 
                                               & vlSelfRef.alu__DOT__b))
                                        : (vlSelfRef.alu__DOT__a 
                                           ^ vlSelfRef.alu__DOT__b));
                            }
                        } else if ((2U & (IData)(vlSelfRef.alu__DOT__op))) {
                            vlSelfRef.alu__DOT__result 
                                = ((1U & (IData)(vlSelfRef.alu__DOT__op))
                                    ? (vlSelfRef.alu__DOT__a 
                                       | vlSelfRef.alu__DOT__b)
                                    : (vlSelfRef.alu__DOT__a 
                                       & vlSelfRef.alu__DOT__b));
                        } else if ((1U & (IData)(vlSelfRef.alu__DOT__op))) {
                            vlSelfRef.alu__DOT__result 
                                = (vlSelfRef.alu__DOT__a 
                                   - vlSelfRef.alu__DOT__b);
                            vlSelfRef.alu__DOT__overflow 
                                = (vlSelfRef.alu__DOT__a 
                                   < vlSelfRef.alu__DOT__b);
                        } else {
                            vlSelfRef.alu__DOT__overflow 
                                = (1U & (IData)((1ULL 
                                                 & (((QData)((IData)(vlSelfRef.alu__DOT__a)) 
                                                     + (QData)((IData)(vlSelfRef.alu__DOT__b))) 
                                                    >> 0x00000020U))));
                            vlSelfRef.alu__DOT__result 
                                = (vlSelfRef.alu__DOT__a 
                                   + vlSelfRef.alu__DOT__b);
                        }
                    } else {
                        vlSelfRef.alu__DOT__result = 0U;
                        vlSelfRef.alu__DOT__zero = 1U;
                        vlSelfRef.alu__DOT__overflow = 0U;
                    }
                    vlSelfRef.zero = vlSelfRef.alu__DOT__zero;
                    vlSelfRef.result = vlSelfRef.alu__DOT__result;
                    vlSelfRef.overflow = vlSelfRef.alu__DOT__overflow;
                }
            }
        }
        Vtop___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VicoIterCount;
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__ico(vlSelfRef.__VicoTriggered, "ico"s);
#endif
            VL_FATAL_MT("/home/virtual/chipship/test_corpus/cocotb_alu/../alu_module/alu.sv", 2, "", "DIDNOTCONVERGE: Input combinational region did not converge after '--converge-limit' of 10000 tries");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        vlSelfRef.__VicoPhaseResult = Vtop___024root___eval_phase__ico(vlSelf);
        vlSelfRef.__VicoFirstIteration = 0U;
    } while (vlSelfRef.__VicoPhaseResult);
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("/home/virtual/chipship/test_corpus/cocotb_alu/../alu_module/alu.sv", 2, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("/home/virtual/chipship/test_corpus/cocotb_alu/../alu_module/alu.sv", 2, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactPhaseResult = Vtop___024root___eval_phase__act(vlSelf);
        } while (vlSelfRef.__VactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Vtop___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");
    }
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");
    }
    if (VL_UNLIKELY(((vlSelfRef.op & 0xf0U)))) {
        Verilated::overWidthError("op");
    }
}
#endif  // VL_DEBUG
