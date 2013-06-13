filetype on
"call pathogen#runtime_append_all_bundles()
filetype plugin indent on

" Allow cursor keys in insert mode
set esckeys

" Enable mouse in all modes
set mouse=a

" Show the filename in the window titlebar
set title

" Enable line numbers
set number

" Centralize backups, swapfiles and undo history
set backupdir=~/.vim/backups
set directory=~/.vim/swaps
if exists("&undodir")
  set undodir=~/.vim/undo
endif

" Don’t add empty newlines at the end of files
set binary
set noeol

set nocompatible
set modelines=0

set guioptions-=M
set guioptions-=r
set guioptions-=L
set guioptions-=T
set ts=4
set softtabstop=4
set shiftwidth=4
set sw=4
set noexpandtab


" do not wrap text & only insert line-breaks
" when return key is hit
set nowrap
set linebreak
set nolist
set textwidth=0
set wrapmargin=0
set formatoptions+=1
"set cindent

set statusline=%<\:%f\ %m%r%y%=%-35.(line:\ %l\ of\ %L,\ col:\ %c%V\ (%P)%)

colorscheme mayansmoke
set guifont=Monaco:h12
set guioptions-=Tr
set autoindent
set showmode
set showcmd
set hidden
set wildmenu
set wildmode=list:longest
set wildignore=*.dll,*.o,*.obj,*.bak,*.exe,*.pyc,*.jpg,*.gif,*.png

set cursorline
set ttyfast
set backspace=indent,eol,start
set laststatus=2
set number
set hlsearch
set showmatch
set autochdir " always keep current working directory
set backspace=indent,eol,start " make backspace a more flexible


map <leader>b :BufExplorer<CR>
map <leader>p :NERDTreeToggle<CR>
map <leader>f :FufFile<CR>

au BufRead,BufNewFile *.php set ft=php.html

inoremap jj <ESC>

if has("win32") || has("win64")
   set directory=$TMP
else
   set directory=~/.vim-tmp
end


function! Preserve(command)
  " Preparation: save last search, and cursor position.
  let _s=@/
  let l = line(".")
  let c = col(".")
  " Do the business:
  execute a:command
  " Clean up: restore previous search history, and cursor position
  let @/=_s
  call cursor(l, c)
endfunction
nmap _$ :call Preserve("%s/\\s\\+$//e")<CR>

