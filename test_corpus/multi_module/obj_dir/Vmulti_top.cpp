// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vmulti_top__pch.h"

//============================================================
// Constructors

Vmulti_top::Vmulti_top(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vmulti_top__Syms(contextp(), _vcname__, this)}
    , clk{vlSymsp->TOP.clk}
    , addr{vlSymsp->TOP.addr}
    , in_b{vlSymsp->TOP.in_b}
    , in_a{vlSymsp->TOP.in_a}
    , alu_out{vlSymsp->TOP.alu_out}
    , reg_out{vlSymsp->TOP.reg_out}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vmulti_top::Vmulti_top(const char* _vcname__)
    : Vmulti_top(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vmulti_top::~Vmulti_top() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vmulti_top___024root___eval_debug_assertions(Vmulti_top___024root* vlSelf);
#endif  // VL_DEBUG
void Vmulti_top___024root___eval_static(Vmulti_top___024root* vlSelf);
void Vmulti_top___024root___eval_initial(Vmulti_top___024root* vlSelf);
void Vmulti_top___024root___eval_settle(Vmulti_top___024root* vlSelf);
void Vmulti_top___024root___eval(Vmulti_top___024root* vlSelf);

void Vmulti_top::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vmulti_top::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vmulti_top___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vmulti_top___024root___eval_static(&(vlSymsp->TOP));
        Vmulti_top___024root___eval_initial(&(vlSymsp->TOP));
        Vmulti_top___024root___eval_settle(&(vlSymsp->TOP));
        vlSymsp->__Vm_didInit = true;
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vmulti_top___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vmulti_top::eventsPending() { return false; }

uint64_t Vmulti_top::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vmulti_top::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vmulti_top___024root___eval_final(Vmulti_top___024root* vlSelf);

VL_ATTR_COLD void Vmulti_top::final() {
    contextp()->executingFinal(true);
    Vmulti_top___024root___eval_final(&(vlSymsp->TOP));
    contextp()->executingFinal(false);
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vmulti_top::hierName() const { return vlSymsp->name(); }
const char* Vmulti_top::modelName() const { return "Vmulti_top"; }
unsigned Vmulti_top::threads() const { return 1; }
void Vmulti_top::prepareClone() const { contextp()->prepareClone(); }
void Vmulti_top::atClone() const {
    contextp()->threadPoolpOnClone();
}
