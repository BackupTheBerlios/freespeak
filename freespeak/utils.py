#     utils.py
#     Fri Jun 14 13:41:56 2004
#     Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
#     http://www.italianpug.org
   
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
    
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Library General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gobject

def syncronized (func):
    def closure (*args, **kwargs):
        def idle (*aargs, **kkwargs):
            func (*aargs, **kkwargs)
            return False
        gobject.idle_add (idle, *args, **kwargs)
    return closure
