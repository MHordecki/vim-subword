" vim_subword by Mike Hordecki
" http://github.com/MHordecki/vim_subword


if exists('g:loaded_vim_subword') || &cp
  finish
endif
let g:loaded_vim_subword = 1

let s:script_dir = fnamemodify(expand("<sfile>"), ":h") . "/../pylibs/vim_subword"
execute "python vim_subword_directory = '" . s:script_dir . "'"
execute "pyfile " . s:script_dir . "/load_me.py"

:nmap di- :py vim_subword.delete_inner_subword()<CR>
:nmap da- :py vim_subword.delete_outer_subword()<CR>
:nmap ci- :py vim_subword.change_inner_subword()<CR>
:nmap ca- :py vim_subword.change_outer_subword()<CR>

